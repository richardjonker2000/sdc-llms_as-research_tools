"""Workshop plumbing: LLM calls, caching, rate limiting and local decision models.

Every answer is looked up in outputs_cached/ first. On a miss we either call the API
(live) or, with DRY_RUN=1, invent a fake but schema-valid answer (no network at all).
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import random
import re
import time
import types
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Union, get_args, get_origin

import pandas as pd
import requests
from dotenv import dotenv_values
from pydantic import BaseModel, ValidationError
from tqdm import tqdm

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "outputs_cached"
KEYS = ["PROVIDER", "API_KEY", "MODEL", "BASE_URL", "RPM", "DRY_RUN", "OLLAMA_URL", "DECISION_MODEL", "REASONING", "OPENALEX_API_KEY", "WORKERS"]
PROVIDERS = {  # name: (base_url, default model)
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai/", "gemini-3.5-flash-lite"),  # Nov 2026: -latest alias hung; full Flash free tier = 20 requests/day
    "minimax_intl": ("https://api.minimax.io/v1", "MiniMax-M3"),
    "minimax_cn": ("https://api.minimax.cn/v1", "MiniMax-M3.1-Flash"),  # new China host (Nov 2026); api.minimaxi.com still works
    "deepseek": ("https://api.deepseek.com", ""),
    "qwen": ("https://dashscope.aliyuncs.com/compatible-mode/v1", ""),
    "modelscope": ("https://api-inference.modelscope.cn/v1", ""),
    "ollama": ("{OLLAMA_URL}/v1", "gemma4:e2b"),
}
CFG: dict[str, Any] = {}


class SetupError(RuntimeError):
    """Something in the setup needs fixing; the message says what."""


# ---------------------------------------------------------------- config
def load_config(env_file: Path | None = None) -> dict[str, Any]:
    """Read config.env (environment variables win) into CFG."""
    file_vals = dotenv_values(env_file or ROOT / "config.env")
    v = {k: (os.environ.get(k) or file_vals.get(k) or "").strip() for k in KEYS}
    provider = (v["PROVIDER"] or "gemini").lower()
    if provider not in PROVIDERS:
        raise SetupError(f"Unknown PROVIDER={provider!r} in config.env. Choose one of: {', '.join(PROVIDERS)}")
    ollama_url = (v["OLLAMA_URL"] or "http://localhost:11434").rstrip("/")
    base, default_model = PROVIDERS[provider]
    CFG.update(
        provider=provider,
        base_url=v["BASE_URL"] or base.format(OLLAMA_URL=ollama_url),
        model=v["MODEL"] or default_model,
        api_key=v["API_KEY"] or ("ollama" if provider == "ollama" else ""),
        rpm=float(v["RPM"] or 10),
        dry_run=v["DRY_RUN"].lower() in ("1", "true", "yes"),
        ollama_url=ollama_url,
        decision_model=v["DECISION_MODEL"] or "tev1:0.8b",
        reasoning=(v["REASONING"] or "low").lower(),
        openalex_key=v["OPENALEX_API_KEY"],
        workers=int(v["WORKERS"] or 4),
    )
    return CFG


def mode() -> str:
    if CFG["dry_run"]:
        return "dry run"
    return "live" if CFG["api_key"] else "cached only"


# ---------------------------------------------------------------- cache + rate limit
def _key(*parts: Any) -> str:
    return hashlib.sha256(json.dumps(parts, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:32]


def _cache_get(key: str) -> dict | None:
    path = CACHE_DIR / f"{key}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _cache_put(key: str, record: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / f"{key}.json").write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")


_recent_calls: list[float] = []
_slot_lock = __import__("threading").Lock()


def _wait_for_slot() -> None:
    """Sliding-window limiter: at most RPM calls in any 60 seconds (safe with parallel requests)."""
    while CFG["rpm"] > 0:
        with _slot_lock:
            now = time.monotonic()
            _recent_calls[:] = [t for t in _recent_calls if now - t < 60]
            if len(_recent_calls) < CFG["rpm"]:
                _recent_calls.append(now)
                return
            wait = 60 - (now - _recent_calls[0]) + 0.1
        time.sleep(wait)


# ---------------------------------------------------------------- generative calls
_client_cache: dict[tuple, Any] = {}


def _extra_params() -> dict:
    """Reasoning settings. MiniMax models think by default: slow, and billed as output tokens.

    REASONING=low (default) | medium | high | max | off. M3.1-Flash cannot switch thinking off (off -> low);
    MiniMax-M3 can (low or off -> no thinking). Other providers: no extra parameters.
    """
    r, m = CFG["reasoning"], CFG["model"]
    if m.startswith("MiniMax-M3.1-Flash"):
        return {"reasoning_effort": "low" if r == "off" else r}
    if m == "MiniMax-M3" and r in ("off", "low"):
        return {"thinking": {"type": "disabled"}}
    return {}


def _call_api(messages: list[dict], temperature: float) -> tuple[str, dict]:
    import openai
    c = CFG
    if not c["api_key"]:
        raise SetupError("No API_KEY. Copy config.example.env to config.env, paste your key after API_KEY=, "
                         "then restart the kernel. (Or set DRY_RUN=1 to practise without a key.)")
    if not c["model"]:
        raise SetupError(f"PROVIDER={c['provider']} has no default model: set MODEL= in config.env.")
    ck = (c["base_url"], c["api_key"])
    if ck not in _client_cache:
        _client_cache[ck] = openai.OpenAI(base_url=c["base_url"], api_key=c["api_key"], max_retries=1, timeout=180)
    _wait_for_slot()
    try:
        resp = _client_cache[ck].chat.completions.create(model=c["model"], messages=messages, temperature=temperature,
                                                         extra_body=_extra_params() or None)
    except openai.AuthenticationError as e:
        raise SetupError(f"API key rejected (401). Check API_KEY in config.env belongs to PROVIDER={c['provider']}.") from e
    except openai.PermissionDeniedError as e:
        raise SetupError(f"Access denied (403) by {c['provider']}. Gemini does not work from mainland China: "
                         "use PROVIDER=minimax_cn there.") from e
    except openai.NotFoundError as e:
        raise SetupError(f"Model {c['model']!r} not found at {c['provider']}. Check MODEL in config.env.") from e
    except openai.APITimeoutError as e:
        raise RuntimeError("The model took longer than 3 minutes to answer. Long answers are slow: "
                           "send less text per request (smaller batches) and try again.") from e
    except openai.APIConnectionError as e:
        raise SetupError(f"Can't reach {c['base_url']}. Check Wi-Fi/VPN (Gemini is blocked in China). "
                         "No internet? Set DRY_RUN=1: cached answers still replay.") from e
    except openai.RateLimitError as e:
        if re.search(r"per ?day|PerDay|RESOURCE_EXHAUSTED.*day", str(e), re.I):
            raise SetupError(f"Daily free quota for {c['model']} is used up. Switch MODEL in config.env "
                             "(e.g. a -lite model), wait until tomorrow, or set DRY_RUN=1 to replay cached answers.") from e
        raise RuntimeError(f"Rate limit (429). Lower RPM in config.env (now {c['rpm']:g}) or wait a minute; "
                           "free tiers also have daily caps.") from e
    usage = resp.usage.model_dump(exclude_none=True) if resp.usage else {}
    return resp.choices[0].message.content or "", usage


def _complete(messages: list[dict], temperature: float, fake) -> tuple[str, str]:
    """Return (raw answer, source) where source is 'cache', 'live' or 'fake'."""
    extra = _extra_params()
    key = _key("chat", CFG["provider"], CFG["model"], messages, temperature, *([extra] if extra else []))
    hit = _cache_get(key)
    if hit is not None:
        _record_usage("cache", hit.get("usage") or {})
        return _log("cache", key) or hit["raw"], "cache"
    if CFG["dry_run"]:
        return _log("fake", key) or fake(), "fake"
    _log("live", key)
    raw, usage = _call_api(messages, temperature)
    _record_usage("live", usage)
    _cache_put(key, {"provider": CFG["provider"], "model": CFG["model"], "temperature": temperature,
                     "params": extra, "messages": messages, "raw": raw, "usage": usage})
    return raw, "live"


USAGE: list[dict] = []   # one row per answer this session (live or from the cache), for cost estimates


def _record_usage(source: str, usage: dict) -> None:
    USAGE.append({"source": source, "tokens_in": usage.get("prompt_tokens", 0),
                  "tokens_out": usage.get("completion_tokens", 0),
                  "thinking": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens", 0)})


def usage_table() -> pd.DataFrame:
    """Token counts of every answer since the kernel started (or since reset_usage()).
    Saved answers keep the counts from the original live call, so the cost is what the run would cost live.
    Fake answers (dry run) are not counted."""
    return pd.DataFrame(USAGE, columns=["source", "tokens_in", "tokens_out", "thinking"])


def reset_usage() -> None:
    USAGE.clear()


def _log(source: str, key: str) -> None:
    """If WORKSHOP_CALL_LOG is set, append one line per generative call (used to count API calls)."""
    if os.environ.get("WORKSHOP_CALL_LOG"):
        with open(os.environ["WORKSHOP_CALL_LOG"], "a", encoding="utf-8") as f:
            f.write(f"{source}\t{key}\n")


def chat(prompt: str, system: str | None = None, temperature: float = 0.0) -> str:
    """Plain-text answer to a prompt."""
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    snippet = re.sub(r"\s+", " ", prompt)[-160:]
    raw = _complete(messages, temperature, lambda: f"[DRY RUN fake answer] ...{snippet}")[0]
    return strip_think(raw)


def strip_think(raw: str) -> str:
    """Remove the <think>...</think> reasoning that thinking models (e.g. MiniMax-M3) put before the answer."""
    return re.sub(r"<think>.*?</think>", "", raw, flags=re.S | re.I).split("</think>")[-1].strip()


def parse_json(raw: str) -> dict:
    """Drop <think> blocks and code fences, then parse the first {...} object."""
    s = re.sub(r"```(?:json)?", "", strip_think(raw))
    start, depth, in_str, esc = s.find("{"), 0, False, False
    if start < 0:
        raise ValueError("No JSON object found in the answer.")
    for i in range(start, len(s)):
        ch = s[i]
        if in_str:
            esc, in_str = (False, in_str) if esc else (ch == "\\", ch != '"')
        elif ch == '"':
            in_str = True
        elif ch in "{}":
            depth += 1 if ch == "{" else -1
            if depth == 0:
                return json.loads(s[start:i + 1])
    raise ValueError("JSON object is not closed.")


@dataclass
class Extraction:
    data: BaseModel | None  # the validated object (None if every attempt failed)
    raw: str                # the model's last raw answer
    attempts: int
    source: str             # 'live', 'cache' or 'fake'
    error: str | None = None

    @property
    def cached(self) -> bool:
        return self.source == "cache"


PROMPT = """{instructions}

Return ONLY one JSON object, no other text, matching this JSON schema:
{schema}

TEXT:
\"\"\"
{text}
\"\"\""""

RETRY = """That answer was not valid:
{error}
Return ONLY the corrected JSON object."""


def extract(text: str, schema: type[BaseModel], instructions: str, temperature: float = 0.0,
            max_retries: int = 2, prompt: str = PROMPT, retry: str = RETRY) -> Extraction:
    """Structured output: ask for JSON, validate with pydantic, retry with the error message.

    `prompt` wraps your instructions ({instructions}, {schema}, {text}); `retry` is sent back with {error}
    when an answer fails validation. Notebook 01 shows both."""
    schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False)
    messages = [{"role": "user", "content": prompt.format(instructions=instructions, schema=schema_json, text=text)}]
    sources, error, raw = [], None, ""
    for attempt in range(1, max_retries + 2):
        rng = random.Random(_key(text, schema_json, attempt, temperature))
        fake = lambda: f"<think>dry run</think>\n```json\n{json.dumps(_fake_obj(schema, text, rng), ensure_ascii=False)}\n```"
        raw, src = _complete(messages, temperature, fake)
        sources.append(src)
        try:
            obj = schema.model_validate(parse_json(raw))
            return Extraction(obj, raw, attempt, _worst(sources))
        except (ValueError, ValidationError) as e:
            error = str(e)[:1500]
            messages = messages + [{"role": "assistant", "content": raw},
                                   {"role": "user", "content": retry.format(error=error)}]
    return Extraction(None, raw, max_retries + 1, _worst(sources), error)


def _worst(sources: list[str]) -> str:
    return next(s for s in ("fake", "live", "cache") if s in sources)


def extract_many(df: pd.DataFrame, text_col: str, schema: type[BaseModel], instructions: str,
                 temperature: float = 0.0, workers: int | None = None, **prompts) -> pd.DataFrame:
    """Run extract() on every row, `workers` requests at a time (within the RPM limit).

    Failed rows get 'error' filled in instead of stopping the loop; a setup problem (no key, no
    connection) stops everything, because it would hit every row.
    """
    from concurrent.futures import ThreadPoolExecutor

    def one(text: str) -> dict:
        try:
            r = extract(text, schema, instructions, temperature, **prompts)   # prompts: prompt=, retry=
            row = r.data.model_dump(mode="json") if r.data else {}
            return row | {"_source": r.source, "_attempts": r.attempts, "error": r.error}
        except SetupError:
            raise
        except Exception as e:  # noqa: BLE001
            return {"_source": "none", "_attempts": 0, "error": f"{type(e).__name__}: {e}"}

    texts = df[text_col].astype(str).tolist()
    with ThreadPoolExecutor(max_workers=max(1, workers or CFG["workers"])) as pool:
        rows = list(tqdm(pool.map(one, texts), total=len(texts), desc=schema.__name__))
    cols = list(schema.model_fields) + ["_source", "_attempts", "error"]
    out = pd.DataFrame(rows, index=df.index).reindex(columns=cols)
    return pd.concat([df.drop(columns=[c for c in cols if c in df.columns]), out], axis=1)


def _fake_value(tp: Any, name: str, text: str, rng: random.Random, field=None) -> Any:
    origin, args = get_origin(tp), get_args(tp)
    words = re.findall(r"\S+", text) or ["example"]
    if origin in (Union, types.UnionType):
        return _fake_value(next(a for a in args if a is not type(None)), name, text, rng, field)
    if origin is Literal:
        return rng.choice(args)
    if origin is dict:
        return {}
    if origin in (list, set, tuple):
        return [_fake_value(args[0] if args else str, name, text, rng) for _ in range(rng.randint(1, 3))]
    if isinstance(tp, type) and issubclass(tp, Enum):
        return rng.choice(list(tp)).value
    if isinstance(tp, type) and issubclass(tp, BaseModel):
        return _fake_obj(tp, text, rng)
    if tp is bool:
        return rng.random() < 0.5
    if tp in (int, float):
        meta = {k: getattr(m, k) for m in (field.metadata if field else []) for k in ("ge", "le") if hasattr(m, k)}
        x = rng.uniform(meta.get("ge", 0), meta.get("le", 80 if tp is int else 1))
        return int(x) if tp is int else round(x, 2)
    if "quote" in name or "evidence" in name:  # mostly real substrings, sometimes invented
        i = rng.randrange(len(words))
        return " ".join(words[i:i + 8]) if rng.random() < 0.8 else "this invention revolutionises everything"
    i = rng.randrange(len(words))
    return " ".join(words[i:i + 3])


def _fake_obj(schema: type[BaseModel], text: str, rng: random.Random) -> dict:
    return {n: _fake_value(f.annotation, n, text, rng, f) for n, f in schema.model_fields.items()}


# ---------------------------------------------------------------- embeddings
EMBED_MODELS = {"minimax_cn": "embo-01", "minimax_intl": "embo-01", "gemini": "gemini-embedding-001"}


def embed(texts: list[str], kind: str = "db", batch: int = 200):
    """Turn texts into meaning-vectors (embeddings) with the provider's embedding model.

    kind: "db" for documents, "query" for a search question (MiniMax treats them slightly differently).
    Raises SetupError in dry-run mode or when the provider has no embedding model.
    """
    import numpy as np
    model = EMBED_MODELS.get(CFG["provider"])
    if CFG["dry_run"] or not model or not CFG["api_key"]:
        raise SetupError(f"No embeddings available (dry run, no key, or none for PROVIDER={CFG['provider']}).")
    out = []
    for i in range(0, len(texts), batch):
        chunk = [t[:2000] or " " for t in texts[i:i + batch]]
        _wait_for_slot()
        if CFG["provider"].startswith("minimax"):  # MiniMax uses its own request format
            r = requests.post(CFG["base_url"].rstrip("/") + "/embeddings", timeout=180,
                              headers={"Authorization": f"Bearer {CFG['api_key']}"},
                              json={"model": model, "texts": chunk, "type": kind})
            j = r.json()
            if not j.get("vectors"):
                raise RuntimeError(f"Embedding request failed: {j.get('base_resp', r.text[:200])}")
            out += j["vectors"]
        else:
            import openai
            client = openai.OpenAI(base_url=CFG["base_url"], api_key=CFG["api_key"], timeout=180)
            out += [d.embedding for d in client.embeddings.create(model=model, input=chunk).data]
    v = np.asarray(out, dtype=np.float32)
    return v / (np.linalg.norm(v, axis=1, keepdims=True) + 1e-9)


# ---------------------------------------------------------------- decision models (local, Ollama)
def _check_questions(questions: dict) -> None:
    if not 1 <= len(questions) <= 64:
        raise ValueError("decide() takes 1 to 64 questions per request.")
    for name, q in questions.items():
        t, crit = q.get("type"), q.get("criteria")
        ok = ((t == "choice" and isinstance(crit, dict) and 2 <= len(crit) <= 26)
              or (t == "noul" and (crit is None or isinstance(crit, dict) and set(crit) == {"false", "true"}))
              or (t == "score" and isinstance(crit, list) and 2 <= len(crit) <= 10))
        if not ok or not q.get("instructions"):
            raise ValueError(f"Question {name!r}: every question needs 'instructions' (the question in words). "
                             "choice needs 2-26 options in a dict, noul optionally {'false': ..., 'true': ...}, "
                             "score needs a list of 2-10 levels (low to high).")


def _fake_decide(questions: dict, rng: random.Random) -> dict:
    """Same shape as the real /v1/systemone answers, with random numbers."""
    def probs(keys):
        w = [rng.random() ** 3 + 1e-3 for _ in keys]
        p = {str(k): x / sum(w) for k, x in zip(keys, w)}
        conf = 1 + sum(x * math.log(x) for x in p.values()) / math.log(len(p))  # 1 - normalised entropy
        return p, conf
    answers = {}
    for name, q in questions.items():
        if q["type"] == "choice":
            p, conf = probs(list(q["criteria"]))
            answers[name] = {"type": "choice", "choice": max(p, key=p.get), "probabilities": p, "confidence": conf}
        elif q["type"] == "noul":
            answers[name] = {"type": "noul", "noul": rng.random()}
        else:
            p, conf = probs(range(len(q["criteria"])))
            answers[name] = {"type": "score", "score": sum(i * x for i, x in enumerate(p.values())),
                             "legend": dict(enumerate(q["criteria"])), "probabilities": p, "confidence": conf}
    return answers


def decide(state: str, questions: dict, use_cache: bool = True) -> dict:
    """Ask a local System One decision model; returns probabilities per question, no text.

    choice -> {'choice', 'probabilities', 'confidence'}; noul -> {'noul': P(true)};
    score -> {'score': expected level 0..n-1, 'probabilities', 'confidence'}.
    confidence is 1 - normalised entropy: 0 = no idea, 1 = certain.
    """
    _check_questions(questions)
    model, url = CFG["decision_model"], f"{CFG['ollama_url']}/v1/systemone"
    body = json.dumps({"model": model, "state": state, "questions": questions}, ensure_ascii=False).encode()
    if len(body) > 64 * 1024:
        raise ValueError("decide() request is over 64 KiB: shorten the text or split the questions.")
    key = _key("decide", model, state, questions)
    hit = _cache_get(key) if use_cache else None
    if hit is not None:
        return hit["answers"]
    if CFG["dry_run"]:
        return _fake_decide(questions, random.Random(key))
    fix = f"In a terminal run:  ollama pull {model}"
    try:
        r = requests.post(url, data=body, headers={"Content-Type": "application/json"}, timeout=120)
    except requests.ConnectionError as e:
        raise SetupError(f"Ollama is not running at {CFG['ollama_url']}. Start the Ollama app. {fix}") from e
    if r.status_code == 404:
        raise SetupError(f"Decision model {model!r} is not installed, or Ollama is too old "
                         f"(update from ollama.com). {fix}")
    if r.status_code >= 400:
        raise RuntimeError(f"Decision model error ({r.status_code}): {r.text[:300]}")
    answers = r.json()["answers"]
    if use_cache:
        _cache_put(key, {"model": model, "state": state, "questions": questions, "answers": answers})
    return answers


def decide_many(texts: list[str], questions: dict, use_cache: bool = True) -> pd.DataFrame:
    """decide() for each text, flattened to one row per text.

    choice -> columns q, q_confidence, q_p_<option>; noul -> q (P(true)); score -> q (expected level).
    """
    rows = []
    for text in tqdm(list(texts), desc="decide"):
        row = {}
        for name, a in decide(text, questions, use_cache).items():
            if a["type"] == "choice":
                row |= {name: a["choice"], f"{name}_confidence": a["confidence"]}
                row |= {f"{name}_p_{k}": v for k, v in a["probabilities"].items()}
            else:
                row[name] = a.get("noul", a.get("score"))
        rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- small helpers
def _norm(s: str) -> str:
    s = str(s).translate(str.maketrans("‘’“”", "''\"\""))
    return re.sub(r"\s+", " ", s).strip().lower()


def quote_check(quote: str, text: str) -> bool:
    """True if the quote appears verbatim in the text (ignoring case and whitespace)."""
    q = _norm(quote).strip(" \"'.…")
    return bool(q) and q in _norm(text)


def ollama_ready() -> str:
    """'ready', 'model missing' or 'not running'."""
    try:
        tags = requests.get(f"{CFG['ollama_url']}/api/tags", timeout=2).json().get("models", [])
    except (requests.RequestException, ValueError):
        return "not running"
    names = {m.get("name", "") for m in tags}
    want = CFG["decision_model"]
    return "ready" if want in names or f"{want}:latest" in names else "model missing"


def status() -> None:
    """Print what the workshop helpers will do with the current config."""
    c = CFG
    explain = {"dry run": "no network; cached answers replay, everything else is FAKE",
               "live": f"cached answers replay, new prompts call the API (max {c['rpm']:g}/min)",
               "cached only": "no API key: only pre-computed answers in outputs_cached/ work"}[mode()]
    if c["dry_run"]:
        dm = "not checked in dry run (fake probabilities)"
    else:
        state = ollama_ready()
        dm = {"ready": "ready", "not running": "Ollama not running (start the Ollama app)",
              "model missing": f"not pulled yet: run  ollama pull {c['decision_model']}"}[state]
    print(f"Provider : {c['provider']}  ({c['base_url']})")
    print(f"Model    : {c['model'] or '(none: set MODEL in config.env)'}")
    print(f"API key  : {'set' if c['api_key'] else 'missing'}")
    print(f"Mode     : {mode().upper()}: {explain}")
    print(f"Decision : {c['decision_model']} @ {c['ollama_url']}: {dm}")
    print(f"Cache    : {len(list(CACHE_DIR.glob('*.json')))} saved answers in outputs_cached/")


load_config()
