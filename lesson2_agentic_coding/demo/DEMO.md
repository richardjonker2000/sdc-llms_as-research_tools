# Lesson 2 (14:00–15:00): run sheet

**The message:** in lesson 1 you ran every step yourself. Here an agent runs them: it owns the code, you own the method. A **skill file** turns a notebook into instructions the agent must follow, checks included.

**Research question** (continues notebook 01, no country comparison): *"I study how AI changes work. I want to know whether AI patents more often automate human work or augment it, and whether that has changed over time. I have the patent data from the workshop (data/patents.csv), the LLM codes from notebook 01 for 100 of the patents (data/patent_codes.csv), and the codebook we used (data/codebook.py). I am not good at Python."*

## Before the session

```bash
./setup.sh --reset-demo --cache-from <MiniPC>:~/projects/sdc_work/outputs_cached   # fresh ~/sdc_agent_demo, saved answers linked in
git clone lesson2_agentic_coding/demo/demo_prepared.bundle ~/sdc_demo_prepared      # the prepared run, one git tag per turn
```

- The saved answers must include the **51 patents the agent codes in S2** (cached on 22 Nov). Then the coding step replays real answers on stage and costs nothing.
- Open four things: terminal **live** (`cd ~/sdc_agent_demo && ./start_agent.sh`), terminal **prepared** (`cd ~/sdc_demo_prepared`), an editor with notebook 01 (Step 1–4) and `.opencode/skills/code-texts/SKILL.md` side by side, and a browser for the output files.
- Start OpenCode once before the session and keep that window open: a new process started within a minute of the last one can hang at startup.

## The hour

| Min | Do | Prepared fallback (`git checkout <tag>`) | Say |
| --- | --- | --- | --- |
| 0–5 | Slide: from notebook to agent. An agent is an LLM + tools (read files, run code) in a loop. | – | "Same methods as this morning. The difference is who presses the buttons." |
| 5–10 | **The agent project.** `AGENTS.md` (who decides what), `opencode.json` (what is blocked). Type `show me config.env`: refused. `data/codebook.py`: the agent may use it, never change it. | – | "No sandbox. An instruction is a request; a permission is enforced." |
| 10–15 | **Notebook → skill.** Notebook 01 next to `code-texts/SKILL.md`: the codebook, the test on 3 rows, the quote check and the cost become *required steps*. Mention `check-agreement` (02) and `cluster-texts` (03). | – | "A skill is your method written down so the agent cannot skip the checks." |
| 15–19 | `/plan` + the research question (about 2 min live). | `t1-plan` | "It looks before it proposes." |
| 19–23 | Read out D1–D3, show of hands. `/revise` with the answers below. | `t2-revise` | "Method questions. It recommends; it doesn't decide." |
| 23–27 | `/next`: S1 builds the dataset (about 2 min). Open `outputs/s1_checks.txt`. It ends by asking **you** to switch live calls on. | `t3-next` | "One step, one report, one commit." |
| 27–33 | Edit `config.env`: `DRY_RUN=0` (the researcher's switch). `/next`: the log shows **`[skill] code-texts`**. Read the report: 0 failed, 0 fake, quote check, value counts, **cost**. On stage the 51 answers replay from the cache, so nothing is spent. | `t4-code` | "Every check from notebook 01, without being asked. And the price." |
| 33–38 | Set `DRY_RUN=1` again. `/extra` LaTeX table (about 3 min). **While it runs**, show the diagram (`t7-diagram`, `outputs/extras/process_diagram.svg`). | `t5-latex`, `t7-diagram` | "The boring parts of a paper are the parts it's best at." |
| 38–42 | **A second skill** (prepared only: 7 min live). `t6-cluster`: themes of the 151 abstracts; `outputs/extras/themes_report.txt`. | `t6-cluster` | "It reports that the groups are not stable. That honesty is in the skill." |
| 42–47 | **The catches** (below). | – | "Checking is still your job." |
| 47–55 | **Write your own skill**: walk through `SKILL_TEMPLATE.md`, fill it in for one example from the room (a codebook coding task for someone's thesis). | – | "If you can write down your method, an agent can follow it." |
| 55–60 | `git log --oneline`. **What goes in your methods section:** `PLAN.md` (decisions, who decided, when), the git log (every step), `CLAIMS.md` (every number → script), the skill file. | – | Delegate environments, bugs, plots, formatting. Never delegate the sample, definitions, codebook or claims. Then Roman at 15:15. |

`/revise` used in the prepared run (adapt to the room's votes):

```
/revise D1: a, AI patents only, and report 'neither' next to it. D2: a, two periods plus the year-by-year figure. D3: c, unknown: it is one download from PatentsView made for the workshop, so every number is a share within this sample. And yes: code the remaining 51 patents with the same codebook (data/codebook.py), so all 151 are comparable. Make that the first step after building the dataset; I will switch live calls on for it.
```

Extras used:

```
/extra Make a LaTeX table for my paper: of the 151 coded patents, how many were labelled automates / augments / neither, split by whether the LLM flagged them as AI. Counts and row percentages.
/extra Group the 151 patent abstracts into themes by their words, with the cluster-texts skill. Use k = 5 and the standard stop words; no LLM naming. I want to see whether the AI patents fall into particular themes.
/extra Make a diagram of what we did, for a slide: from the 151 patents, to notebook 01's 100 codes plus the 51 new ones with the same codebook, to the table and the themes. Put the real counts on the boxes.
```

Times per turn in the prepared run (MiniMax M3.1 Flash, 22 Nov): plan 1.9 min, revise 1.2, next 1.9, coding 4.6 (48 live calls; on stage they replay), LaTeX 2.9, themes 6.8, diagram 4.9.

## The catches (they really happened)

- **"Re-code 10 to check."** After `/revise` the agent proposes re-coding 10 of the old patents live, to test whether the two halves are comparable (D5). Sounds rigorous. But identical prompts replay the saved answer, so it would get 100% agreement for free. *Ask the room what is wrong with the check before you say it.*
- **It went looking where it shouldn't.** In the first test run the agent opened the folder of saved answers to work out which patents were already coded, and ran out of steps. Now that folder is blocked in `opencode.json`. The rule in `AGENTS.md` alone would not have stopped it.
- **"Checked" is not checked.** In an earlier run the LaTeX table had `9 (81.8)\%` instead of `9 (81.8\%)`, and the agent reported "checked": it checked the numbers, not the formatting.
- **It notices limits, if the skill asks.** The themes are no more stable than random groups (22% vs 22% of pairs stay together), and it says so, with the patent boilerplate words ("one", "least", "plurality") as the likely cause.

## Numbers to have in mind

- Coded patents: 151 (100 from notebook 01, 51 by the agent). AI: 58. Among AI patents: 43 automate, 7 augment, 8 neither.
- Quote check: 97 of 100 (notebook 01), 50 of 51 (agent).
- Cost of coding 51 patents live: ¥0.07; about ¥15 per 10,000 texts.

## If something goes wrong

- **No output after about 60 s:** Ctrl-C, start again, or switch to the prepared tag.
- **No network or the key fails:** prepared tags plus `transcripts/` cover every step.
- **A permission dialog pops up:** click deny. That is the rule working; say so.
- **It asks different decisions than D1–D3:** answer those. The prepared tags still follow the run above.
