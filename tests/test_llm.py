import socket
from typing import Literal

import pandas as pd
import pytest
from pydantic import BaseModel, Field

from workshop import llm


class Code(BaseModel):
    is_ai: bool
    domain: Literal["health", "finance", "other"]
    min_age: int = Field(ge=18, le=99)
    evidence_quote: str


TEXT = "A neural network detects tumours in chest X-ray images for hospital radiologists."


@pytest.fixture
def dry(monkeypatch, tmp_path):
    """Dry-run mode, empty cache, and any attempt to open a socket fails the test."""
    monkeypatch.setenv("DRY_RUN", "1")
    monkeypatch.setenv("API_KEY", "")
    monkeypatch.setattr(llm, "CACHE_DIR", tmp_path)
    llm.load_config()

    def no_network(*a, **k):
        raise AssertionError("network used in dry run")
    monkeypatch.setattr(socket.socket, "connect", no_network)
    yield
    monkeypatch.undo()
    llm.load_config()


@pytest.fixture
def live(monkeypatch, tmp_path):
    """Pretend-live mode: the API call is replaced by a scripted list of answers."""
    monkeypatch.setenv("DRY_RUN", "0")
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setattr(llm, "CACHE_DIR", tmp_path)
    llm.load_config()
    calls = []

    def script(answers):
        def fake_call(messages, temperature):
            calls.append(messages)
            return answers[len(calls) - 1], {}
        monkeypatch.setattr(llm, "_call_api", fake_call)
        return calls
    yield script
    monkeypatch.undo()
    llm.load_config()


# ---- JSON cleaning
def test_parse_json_think_and_fences():
    raw = '<think>Let me think {not json}</think>\nSure!\n```json\n{"a": 1, "b": {"c": "x}y"}}\n```\nDone.'
    assert llm.parse_json(raw) == {"a": 1, "b": {"c": "x}y"}}


def test_parse_json_unclosed_think_and_escaped_quote():
    assert llm.parse_json('reasoning...</think>{"q": "he said \\"hi\\" {"}') == {"q": 'he said "hi" {'}


def test_parse_json_errors():
    with pytest.raises(ValueError):
        llm.parse_json("no json here")
    with pytest.raises(ValueError):
        llm.parse_json('{"a": 1')


# ---- quote checking
@pytest.mark.parametrize("quote, ok", [
    ("neural network detects", True),
    ("NEURAL   network\n detects", True),
    ('"chest X-ray images."', True),
    ("deep learning model", False),
    ("", False),
])
def test_quote_check(quote, ok):
    assert llm.quote_check(quote, TEXT) is ok


# ---- dry-run mode
def test_dry_run_chat_and_extract(dry):
    assert "DRY RUN" in llm.chat("hello")
    r = llm.extract(TEXT, Code, "Code this.")
    assert isinstance(r.data, Code) and r.source == "fake" and r.attempts == 1
    assert 18 <= r.data.min_age <= 99


def test_dry_run_extract_many(dry):
    df = pd.DataFrame({"id": [1, 2, 3], "text": [TEXT, "Banking app.", "A chair."]})
    out = llm.extract_many(df, "text", Code, "Code this.")
    assert len(out) == 3 and out["error"].isna().all()
    assert {"id", "is_ai", "domain", "_source"} <= set(out.columns)


QS = {"exposed": {"type": "choice", "instructions": "How exposed is this task to LLMs?",
                  "criteria": {"high": "a", "medium": "b", "low": "c"}},
      "routine": {"type": "noul", "instructions": "Is this task routine?"},
      "skill": {"type": "score", "instructions": "How much skill does it need?", "criteria": ["low", "mid", "high"]}}


def test_dry_run_decide_matches_real_shape(dry):
    a = llm.decide(TEXT, QS)
    p = a["exposed"]["probabilities"]
    assert abs(sum(p.values()) - 1) < 1e-6 and a["exposed"]["choice"] == max(p, key=p.get)
    assert 0 <= a["exposed"]["confidence"] <= 1
    assert 0 <= a["routine"]["noul"] <= 1 and 0 <= a["skill"]["score"] <= 2
    assert set(a["skill"]["probabilities"]) == {"0", "1", "2"}


def test_decide_rejects_bad_questions(dry):
    with pytest.raises(ValueError):
        llm.decide(TEXT, {"q": {"type": "choice", "instructions": "x?", "criteria": {"only": "one"}}})
    with pytest.raises(ValueError):  # instructions are required by the server
        llm.decide(TEXT, {"q": {"type": "noul"}})


# ---- cache and retries (no real network: API call is scripted)
def test_live_answers_are_cached(live):
    calls = live(["first answer"])
    assert llm.chat("hi") == "first answer"
    assert llm.chat("hi") == "first answer" and len(calls) == 1
    llm.CFG["dry_run"] = True  # cached answers still replay in dry run
    assert llm.chat("hi") == "first answer"


def test_extract_retries_with_error(live):
    good = '{"is_ai": true, "domain": "health", "min_age": 18, "evidence_quote": "neural network"}'
    calls = live(['{"is_ai": true, "domain": "space"}', good])
    r = llm.extract(TEXT, Code, "Code this.")
    assert r.data.domain == "health" and r.attempts == 2 and r.source == "live"
    assert "not valid" in calls[1][-1]["content"]


def test_config_example_parses(monkeypatch):
    for k in llm.KEYS:
        monkeypatch.delenv(k, raising=False)
    cfg = llm.load_config(llm.ROOT / "config.example.env")
    assert cfg["provider"] == "minimax_cn" and cfg["model"] == "MiniMax-M3.1-Flash"
    assert cfg["rpm"] == 60 and cfg["dry_run"] is False and cfg["decision_model"] == "tev1:0.8b"
    monkeypatch.undo()
    llm.load_config()


def test_chat_strips_think(live):
    live(["<think>We need to answer briefly.</think>\n\nConnection OK"])
    assert llm.chat("hi") == "Connection OK"


def test_reasoning_params(monkeypatch):
    llm.CFG.update(model="MiniMax-M3.1-Flash", reasoning="low")
    assert llm._extra_params() == {"reasoning_effort": "low"}
    llm.CFG.update(reasoning="off")
    assert llm._extra_params() == {"reasoning_effort": "low"}  # Flash cannot switch thinking off
    llm.CFG.update(model="MiniMax-M3")
    assert llm._extra_params() == {"thinking": {"type": "disabled"}}
    llm.CFG.update(model="gemini-3.5-flash-lite")
    assert llm._extra_params() == {}
    llm.load_config()
