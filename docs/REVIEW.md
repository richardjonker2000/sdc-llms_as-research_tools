# Review guide for Roman: Session 1 (Richard, 09:45–10:45)

Thanks for looking this over. This page says what the session is, how to set it up in about 15 minutes, and what I'd most like your eyes on. Everything below is on `main`.

## The session in one table

Demo first, as you suggested: students watch, and follow along on their laptops only if they like.

| Time | Block | Material |
| --- | --- | --- |
| 09:45 | Welcome, the three blocks | intro slide (ask me for the link) |
| 09:48 | Coding with a codebook: patent abstracts become a validated table, quote by quote | `lesson1_text_to_data/01_codebook_extraction.ipynb` |
| 10:08 | Mapping a field: one research question becomes a map of the literature | `lesson1_text_to_data/08_bibliometrics.ipynb` |
| 10:15 | A coding agent: it writes the code, the researcher makes every method decision. Includes your "tricks" idea: a LaTeX table and a diagram made by the agent | `lesson2_agentic_coding/demo/DEMO.md` |
| 10:45 | End | – |

Notebook 03 (decision models, `tev1`) is dropped from the session and is now self-study, as are 00, 02, 04–07 and 09. The full timing and talking points are in `docs/facilitator_notes.md`.

## Option A: a 15-minute read (no setup)

Read these on GitHub, in this order:

1. `docs/facilitator_notes.md`: the timing plan and the "wow moments" for 01.
2. `lesson1_text_to_data/01_codebook_extraction.ipynb`: the codebook, the full prompt (`INSTRUCTIONS`, `TEMPLATE`, `RETRY` are all visible now), the quote check, the figure.
3. `lesson2_agentic_coding/demo/DEMO.md`: the 30-minute agent run sheet, minute by minute.
4. `lesson2_agentic_coding/demo/transcripts/`: what the agent actually did in the prepared run, one file per turn (`t1-plan.txt` … `t7-fix.txt`). These are readable without installing anything.
5. `lesson2_agentic_coding/agent_harness/AGENTS.md` and `lesson2_agentic_coding/agent_harness/opencode.json`: the agent's rules and permissions.

## Option B: run it (macOS or Linux, about 15 minutes)

```bash
git clone git@github.com:richardjonker2000/sdc-llms_as-research_tools.git
cd sdc-llms_as-research_tools
./setup.sh --no-ollama                # Python env, config.env (asks for the key, hidden), OpenCode, ~/sdc_agent_demo
```

- `./setup.sh --help` lists the options. Add `--china` for a PyPI mirror.
- The saved model answers (`outputs_cached/`, 68 MB) are not in git. Without them, notebooks 01 and 08 either call the API live (about 200 calls in total) or, with `DRY_RUN=1`, show clearly marked fake answers. Ask me for the zip, then run `./setup.sh --cache-from <folder>`.
- `--no-ollama` skips Ollama and the decision model (about 3.3 GB), which only notebook 03 needs. 03 isn't in the session.
- The key goes in `config.env` (`PROVIDER=minimax_cn`, `API_KEY=`); `setup.sh` asks for it and never prints it.

**Notebooks:** `source .venv/bin/activate && jupyter lab`, then open 01 and 08.

**The prepared agent run** (no key needed): every agent turn is a git tag you can step through.

```bash
git clone lesson2_agentic_coding/demo/demo_prepared.bundle ~/sdc_demo_prepared
cd ~/sdc_demo_prepared && git log --oneline --decorate
git checkout t1-plan     # then t2-revise, t3-next, t4-diagram, t5-latex, t6-explain, t7-fix
```

Look at `PLAN.md` after `t1-plan` and `t2-revise`, at `outputs/extras/pipeline.svg` after `t4-diagram`, and at `outputs/extras/automation_by_ai.tex` after `t5-latex` and `t7-fix`.

**The live agent** (needs a key): `cd ~/sdc_agent_demo && ./start_agent.sh`, then follow the "/plan …" line in `lesson2_agentic_coding/demo/DEMO.md`. Each turn takes 1.5–2 minutes.

## What I'd most like feedback on

1. **Pace.** Is 20 minutes for notebook 01 and 7 for bibliometrics realistic for master's and PhD students who mostly watch?
2. **The agent's research question** (automate vs augment in AI patents, and change over time). Is it a good showcase, and is it safe for the audience? There's no country comparison any more.
3. **The decisions the agent raises** after `/plan` (D1–D3 in `t1-plan`). Are they the right method questions to put to the room for a vote?
4. **The "spot the bug" moment.** In the prepared LaTeX table, the agent wrote `9 (81.8)\%` and called it "checked". On stage the room finds it, then I show the agent's fix. Does that land, or does it undercut the message?
5. **Overlap with your sessions** (11:15 qualitative coding, 15:35 what's possible now in qualitative workflows). Anything I should leave to you, or set up for you?
6. **Anything sensitive** for the China audience that I've missed in the data or the examples.

## Known open items

- **Keys.** The prepared agent runs and smoke tests used your MiniMax key. The workshop will get its own pay-as-you-go key, after which you may want to rotate yours. No key is in the repo, the notebooks, the bundle or the transcripts.
- **Not yet tested from inside China:** the API calls and the PyPI mirror.
- **Draft labels.** `data/gold_onet.csv` (used by notebook 03 only) still has draft labels.
- **Live agent speed.** One known hiccup: a new OpenCode process started within a minute of the last can hang at startup. On stage it's one window kept open, and the run sheet says what to do if it stalls.

Comments as GitHub issues, PR comments or a message are all fine.
