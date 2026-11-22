# From text to dataset: LLMs as research tools

SDC workshop *New Tools, Old Questions* · Wed 25 Nov 2026 · Sino-Danish Center, UCAS Yanqihu Campus

Two hands-on lessons. No coding experience needed.

| | Lesson | Folder |
| --- | --- | --- |
| 11:30–12:30 | **1 · What LLMs can do with text:** coding with a codebook, checking it, mapping a field | `lesson1_text_to_data/` |
| 14:00–15:00 | **2 · Agentic coding:** working with a coding agent, and skill files you can reuse | `lesson2_agentic_coding/` |

No coding at all? Use `lesson1_text_to_data/prompts_chatbot_track.md` in any chatbot.

**Organisers:** `docs/PRESENTER_GUIDE.md` is the script for the session (every prompt, what to say), `docs/REVIEW.md` the review guide for co-organisers, `docs/facilitator_notes.md` the timing and likely questions.

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

## 2 · Local decision model (Ollama, optional)

Only needed for notebook 03, which is self-study and not part of the session. Skip this step if you are short of time or disk space.

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

Then open `lesson1_text_to_data/00_setup.ipynb` and run it. You should see **Connection OK**.

## 4 · Troubleshooting

| You see | Fix |
| --- | --- |
| `No module named 'workshop'` or `'openai'` | Start Jupyter from this folder with the environment activated (step 1), and open notebooks from `lesson1_text_to_data/`. |
| `No API_KEY` | Create `config.env` (step 3), then **Kernel ▸ Restart Kernel**. Changes to `config.env` need a restart. |
| `API key rejected (401)` | The key doesn't belong to the `PROVIDER` you set. Check both lines. |
| `Can't reach ...` / `Access denied (403)` | No internet, or a blocked provider: Gemini does not work from mainland China, so use `minimax_cn`. Offline? Set `DRY_RUN=1`. |
| `Model ... not found` / `has no default model` | Set `MODEL=` to a model your provider offers (check its website). |
| `Rate limit (429)` / `Daily free quota ... used up` | Free tiers cap calls per minute **and per day** (Gemini Flash: only 20 a day in Nov 2026; each model has its own quota). Lower `RPM`, switch `MODEL`, or wait. Saved answers are never lost. |
| `Ollama is not running` | Start the Ollama app (look for the llama icon), then re-run the cell. |
| `Decision model ... not installed` | Run `ollama pull tev1:0.8b`. If the pull says "requires a newer version", update Ollama. |

Anything in the `error` column of a results table is a single row that failed, while the rest of the run carried on.

## 5 · What's here

```
lesson1_text_to_data/      Lesson 1 (11:30): what LLMs can do with text. Notebooks 00–09, no-code chatbot track
lesson2_agentic_coding/    Lesson 2 (14:00): agentic coding and skill files
  agent_harness/           a starter project for a coding agent (OpenCode): rules, permissions, commands
  demo/                    the prepared agent run and its run sheet (organisers)
workshop/                  shared helper code used by the notebooks (llm.py, biblio.py, style.py)
data/                      all datasets, see data/README.md
outputs/                   your results
outputs_cached/            saved answers for offline replay (not in git)
docs/                      organisers: presenter guide, facilitator notes, review guide, China deployment, slides
setup.sh · make_cache.py   one-shot setup for a demo laptop · fills outputs_cached/ (organisers)
tools/ · tests/            how the data and notebooks were built · pytest
```

`outputs_cached/` (saved answers and embeddings, ~66 MB) is not in git: build it with `make_cache.py` or get it from the organisers.

## Attribution

This workshop includes information from the O\*NET 31.0 Database by the U.S. Department of Labor, Employment and Training Administration (USDOL/ETA). Used under the CC BY 4.0 license. O\*NET® is a trademark of USDOL/ETA. The workshop organisers have modified all or some of this information. USDOL/ETA has not approved, endorsed, or tested these modifications. Patent data: USPTO via PatentsView (CC BY 4.0). Clinical trials: ClinicalTrials.gov. Interview snippets are synthetic.
