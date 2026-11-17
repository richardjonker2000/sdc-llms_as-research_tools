# LLMs as research tools: Session 1 materials

SDC workshop *New Tools, Old Questions* · Session 1 · Wed 25 Nov 2026 · Sino-Danish Center, UCAS Yanqihu Campus

Hands-on notebooks showing what LLMs can do with research text: codebook-driven extraction, consistency checks, local decision models, long-document extraction, rewriting, and your own data. No coding experience needed. No coding at all? Use `prompts_chatbot_track.md` in any chatbot.

## 1 · Install (10 minutes, before the session)

**Organisers / demo laptop (macOS or Linux):** `./setup.sh` does everything below (Python packages, `config.env`, Ollama + `tev1`, a notebook 00 check) plus OpenCode and a ready agent demo folder; add `--cache-from <path>` to copy `outputs_cached/` (`./setup.sh --china` uses a PyPI mirror; `--help` for options). Participants follow the steps by hand.

You need **Python 3.10, 3.11 or 3.12**. Check with `python --version` (Windows) or `python3 --version` (macOS). If you don't have it, get it from python.org; on Windows, tick *"Add python.exe to PATH"*.

Open a terminal (Windows: *Command Prompt*; macOS: *Terminal*) in this folder:

| | Windows | macOS |
| --- | --- | --- |
| Create environment | `python -m venv .venv` | `python3 -m venv .venv` |
| Activate it | `.venv\Scripts\activate` | `source .venv/bin/activate` |
| Install packages | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| Start Jupyter | `jupyter lab` | `jupyter lab` |

**In mainland China** pip is faster with a mirror: `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

## 2 · Local decision model (Ollama)

1. Install the **latest Ollama** from [ollama.com/download](https://ollama.com/download) (tested with 0.40.15; version 0.35 is too old for `tev1`).
2. Start the Ollama app, then in a terminal run: `ollama pull tev1:0.8b` (833 MB, once).

No Ollama? Notebook 03 still replays saved answers, and every other notebook works without it.

## 3 · Settings: `config.env`

Copy `config.example.env` to `config.env` and fill in two lines:

```
PROVIDER=minimax_cn     # in Beijing; gemini works outside China
API_KEY=your-key-here
```

Other providers: `minimax_intl`, `deepseek`, `qwen`, `modelscope` (free daily quota), `ollama`. For deepseek, qwen and modelscope also set `MODEL=`. Your key stays in `config.env` and never appears in a notebook. Never share that file.

**Three modes.** *Live*: new prompts call the API. *Cached*: answers already in `outputs_cached/` replay instantly in every mode. *Dry run* (`DRY_RUN=1`): no network at all; anything not cached gets a **fake** answer with the right format, so every cell still runs.

Then open `notebooks/00_setup.ipynb` and run it. You should see **Connection OK**.

## 4 · Troubleshooting

| You see | Fix |
| --- | --- |
| `No module named 'workshop'` or `'openai'` | Start Jupyter from this folder with the environment activated (step 1), and open notebooks from `notebooks/`. |
| `No API_KEY` | Create `config.env` (step 3), then **Kernel ▸ Restart Kernel**. Changes to `config.env` need a restart. |
| `API key rejected (401)` | The key doesn't belong to the `PROVIDER` you set. Check both lines. |
| `Can't reach ...` / `Access denied (403)` | No internet, or a blocked provider: Gemini does not work from mainland China, so use `minimax_cn`. Offline? Set `DRY_RUN=1`. |
| `Model ... not found` / `has no default model` | Set `MODEL=` to a model your provider offers (check its website). |
| `Error 529` / `InternalServerError` / `负载较高` | The provider's servers are overloaded (common at busy times). Not your setup: wait half a minute and re-run the cell. Rows already coded are saved. |
| `Rate limit (429)` / `Daily free quota ... used up` | Free tiers cap calls per minute **and per day** (Gemini Flash: only 20 a day in Nov 2026; each model has its own quota). Lower `RPM`, switch `MODEL`, or wait. Saved answers are never lost. |
| `Ollama is not running` | Start the Ollama app (look for the llama icon), then re-run the cell. |
| `Decision model ... not installed` | Run `ollama pull tev1:0.8b`. If the pull says "requires a newer version", update Ollama. |

Anything in the `error` column of a results table is a single row that failed, while the rest of the run carried on.

## 5 · What's here

`notebooks/` the 8 notebooks (00–07) plus the bibliometrics add-on: 08 maps a field from a topic, 09 adds more lenses (OpenAlex data in `data/openalex/`; 08 and 09 also need `OPENALEX_API_KEY` in `config.env` to search your own topic) · `workshop/` helper code (`llm.py`) · `data/` all datasets, see `data/README.md` · `outputs/` your results · `outputs_cached/` saved answers · `prompts_chatbot_track.md` no-code version · `facilitator_notes.md` session plan · `make_cache.py` fills the cache (organiser) · `tools/` how the data and notebooks were built · `tests/` run with `pip install pytest && pytest`. · `agent_harness/` coding-agent session (OpenCode), see its README · `docs/DEPLOYMENT_CHINA.md` China deployment notes and local requirements.

`outputs_cached/` (saved answers and embeddings, ~66 MB) is not in git: build it with `make_cache.py` or get it from the organisers.

## Attribution

This workshop includes information from the O\*NET 31.0 Database by the U.S. Department of Labor, Employment and Training Administration (USDOL/ETA). Used under the CC BY 4.0 license. O\*NET® is a trademark of USDOL/ETA. The workshop organisers have modified all or some of this information. USDOL/ETA has not approved, endorsed, or tested these modifications. Patent data: USPTO via PatentsView (CC BY 4.0). Clinical trials: ClinicalTrials.gov. Interview snippets are synthetic.
