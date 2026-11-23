# Organisers

Everything participants don't need. One page for the day; the rest is how the materials were built.

```
README.md          this page: the day, the checklist, fallbacks, likely questions, open items
demo/              lesson 2: DEMO.md (the run sheet), demo_prepared.bundle (one git tag per turn), transcripts.md
build/             make_cache.py, build_notebooks.py + nb_src/ (notebook sources), fetch_*.py (how data/ was built)
tests/             python -m pytest organisers/tests
```

## The day (Wed 25 Nov)

| Time | Who | What | Script |
| --- | --- | --- | --- |
| 10:45 | Roman | Overview: classifiers → embeddings → LLMs → agents | – |
| 11:30 | Richard | **Lesson 1 · From text to dataset** (notebooks 01–04) | `../lesson1_text_to_data/README.md` (minute plan, costs) |
| 14:00 | Richard | **Lesson 2 · Agentic coding and skill files** (demo) | `demo/DEMO.md` |
| 15:15 | Roman | Agents and qualitative work | – |

## Before the day

- [ ] `git pull`, then `./setup.sh --reset-demo --cache-from <MiniPC>:~/projects/sdc_work/outputs_cached` (fresh agent folder, all saved answers including the 51 the agent codes).
- [ ] `git clone organisers/demo/demo_prepared.bundle ~/sdc_demo_prepared` (the prepared agent run).
- [ ] `config.env` has the **workshop** key, never Roman's. Notebooks can stay on `DRY_RUN=0` (they replay saved answers anyway); the agent folder stays on `DRY_RUN=1`.
- [ ] Run 01–04 top to bottom once: every cell should be a cache hit and the cost lines should say ¥0.
- [ ] Start the agent once (`cd ~/sdc_agent_demo && ./start_agent.sh`) and keep that window open.
- [ ] Jupyter server for participants: the repo, `outputs_cached/` and a `config.env` (workshop key, or `DRY_RUN=1` with no key).
- [ ] If the folder goes out on USB: include `outputs_cached/` (not in git, ~66 MB).

## On the day: if something breaks

| Problem | Do |
| --- | --- |
| Wi-Fi dies | `DRY_RUN=1` in `config.env`, **Kernel ▸ Restart Kernel**. Saved answers replay; anything new is clearly marked fake. Agent: switch to the prepared tags. |
| Rate limits (429) | Lower `RPM` in `config.env`, restart the kernel. Re-running a cell only calls the API for rows that failed. |
| The agent hangs at start | Ctrl-C, start again, or the prepared tag. See `demo/DEMO.md`. |
| `pip` slow in China | `./setup.sh --china`, or `-i https://pypi.tuna.tsinghua.edu.cn/simple` (fallback `https://mirrors.aliyun.com/pypi/simple/`). |

Providers from China: `minimax_cn` (default), `deepseek`, `qwen`, `modelscope` work; `gemini` is blocked. Hugging Face is blocked, but only `build/fetch_patents.py` uses it.

## Likely questions

- **Is it reproducible?** Not by default: models change and sampling is random. Cache everything with provider, model and prompt; archive the cache with the paper; report model and date.
- **Confidential data?** Not with a cloud API unless the data agreement allows it. Local models (`PROVIDER=ollama`, A6) keep data on the machine.
- **How many to hand-code?** Enough to estimate agreement per category, often 100–300. A model agreeing with another model is not validation (notebook 02).
- **Which model is best?** It changes monthly. Validate on your own task.
- **Temperature 0 is not deterministic?** Correct: providers batch requests. Caching freezes one answer.
- **Cost?** Every notebook prints it. About ¥5–15 per 10,000 texts with MiniMax M3.1 Flash.
- **Chinese text?** Yes. Keep the categories fixed; test on a few rows first.

## Open items

- The workshop's own pay-as-you-go key; test it from inside China (`minimax_cn`, and the agent's `minimax-cn` provider in `start_agent.sh -m`).
- OpenAlex, OpenCode's startup fetch from `models.dev`, and GitHub from the campus network: untested in China. Fallbacks: the data is in `data/`, the agent has the prepared run.
- Agent on Windows: the permission allowlist matches `.venv/bin/python`, not `.venv\Scripts\python.exe`. Only matters if participants run the agent themselves.
- Roman's key: rotate after testing.

## Rebuilding

- Notebooks: edit `build/nb_src/<name>.txt`, then `python organisers/build/build_notebooks.py <prefix>` (files starting with `A` go to `additional_materials/`).
- Saved answers: `python organisers/build/make_cache.py` with a live key (fills `outputs_cached/`).
- Data: `build/fetch_*.py` and `build/build_onet.py`; provenance in `../data/README.md`.
- An agent turn as text: `python organisers/build/show_turn.py <opencode-run.jsonl>`.
