# Agent demo (10:40–10:55): run sheet

**The message:** the agent handles the code; you make every method decision, and you can check everything it did.

**Research question** (no country comparison): *"I study how AI changes work. I want to know whether AI patents more often automate human work or augment it, and whether that has changed over time. I have the patent data from the workshop (data/patents.csv) and the LLM codes from notebook 01 (data/patent_codes.csv). I am not good at Python."*

## Before the session

```bash
./setup.sh                                   # builds ~/sdc_agent_demo (DRY_RUN=1, git, start_agent.sh)
git clone agent_harness/demo_prepared.bundle ~/sdc_demo_prepared    # the prepared run, one git tag per turn
cp -r ~/sdc_agent_demo/.venv ~/sdc_agent_demo/config.env ~/sdc_demo_prepared/   # only if you continue live from a tag
```

Open three terminal tabs: **live** (`cd ~/sdc_agent_demo && ./start_agent.sh`), **prepared** (`cd ~/sdc_demo_prepared`), and an editor or browser for the files.
Start OpenCode once before the session so it has fetched its model list. Then keep the same OpenCode window open: starting a new process within a minute of the last one can hang at startup.

## The 15 minutes

| Min | Do | Prepared fallback (`git checkout <tag>`) | Say |
| --- | --- | --- | --- |
| 0–2 | Show `AGENTS.md` (who decides what), `opencode.json` (no web, can't read `config.env`, can't touch `workshop/`, can't delete or rewrite git), `git log`. | – | "There's no sandbox. These rules are the control. An instruction is a request; a permission is enforced." |
| 2–5 | `/plan` + the research question. Talk through its steps: it looks at the data with one script before proposing anything. If it tries `cat config.env`, point at the block. | `t1-plan`: `PLAN.md` and the transcript `demo_transcript/t1-plan.txt` | "It is looking before it proposes." |
| 5–8 | Read out D1–D3 and take a show of hands. Then: `/revise D1: b, ... D2: a ..., D3: a ...` | `t2-revise` | "Method questions. It recommends; it doesn't decide." |
| 8–11 | `/next` → step S1 and its report. Open `outputs/analysis_dataset.csv`. | `t3-next` | "One step, one report, one commit. Please check: …" |
| 11–14 | `/extra Make a LaTeX table …` (about 1.5 min live). **While it runs**, show the prepared diagram (`t4-diagram`, `outputs/extras/pipeline.svg`). | `t5-latex`, `outputs/extras/automation_by_ai.tex` | "The boring parts of a paper are the parts it's best at." |
| 14–15 | `git log --oneline`. | – | Delegate environments, bugs, plots, formatting. Never delegate the sample, definitions, codebook or claims. |

Times per turn in the prepared run (MiniMax M3.1 Flash, Nov 18): plan 2.0 min, revise 1.4, next 1.6, diagram 2.2, LaTeX 1.6.

## Moments to point at (they really happened)

- **The check it skipped.** In the prepared LaTeX table, the percent sign is outside the bracket: `9 (81.8)\%` instead of `9 (81.8\%)`. The agent reported "checked" (it checked the numbers, not the formatting). Ask the room to spot it before you say it.
- **"Verbatim".** In one smoke-test run the agent wrote "30 verbatim quotes" in a diagram; only 29 of 30 are in the abstracts. The rule "never claim what no script checked" came from that.
- **D4 after `/revise`: "paste notebook 01's prompt".** Notebook 01 isn't in its folder, so it asks for the codebook text. Notebook 01 now shows that text in full (`INSTRUCTIONS`, `TEMPLATE`, `RETRY`). Same codebook, comparable codes.
- **The decisions are the right ones**: whether to code the other 121 patents, what "neither" means, what "over time" means with 3–6 coded patents per year. It also asks how the 30 were sampled (random, `random_state=1`).

## If something goes wrong

- **No output after about 60 s:** Ctrl-C, start again, or switch to the prepared tag.
- **No network or the key fails:** prepared tags plus `demo_transcript/` cover every step.
- **It gets blocked and stops:** that's the rule working. Say so, then `/next` or the prepared tag.
