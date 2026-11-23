# Agent harness: the agent owns the code, the researcher owns the method

A starter project for a coding agent ([OpenCode](https://opencode.ai)) on a real dataset: 151 USPTO patents, notebook 01's LLM codes for 100 of them, and the codebook that made them.

- **The agent** fixes code problems on its own: environments, bugs, plots, formatting.
- **The researcher** decides every method choice: sample, definitions, codebook, LLM use, statistics.

There is no sandbox. The control comes from OpenCode's permissions and instructions:

| File | What it does |
| --- | --- |
| `AGENTS.md` | Roles, the code-vs-method split, the workflow, the `PLAN.md` template, the report format, hard rules |
| `opencode.json` | Permissions: no web, no edits outside the agent's folders, a bash allowlist; reading `config.env` or the saved answers is denied |
| `.opencode/agents/` | `planner` (writes only `PLAN.md`, ends with decisions D1, D2, …) and `builder` (one plan step, a report, a commit) |
| `.opencode/commands/` | `/plan <idea>`, `/revise <answers>`, `/next`, `/extra <job>`, `/explain`, `/status` |
| `.opencode/skills/` | `code-texts`, `check-agreement`, `cluster-texts`: lesson 1 notebooks 01–03 as skills |
| `data/codebook.py` | Notebook 01's codebook, word for word: the agent imports it and may not change it |

## The loop

1. `/plan My research idea ...` → `PLAN.md` with open decisions.
2. `/revise D1: a, D2: ...` → repeat until happy.
3. `/next` → one step, a short report ("Please check: ..."), and a git commit. Repeat.

## Run it

From the main folder: `./setup.sh`. It copies this folder to `~/sdc_agent_demo` together with `workshop/` and `data/patents.csv`, makes it a git project with its own `.venv` and `DRY_RUN=1`, and writes `start_agent.sh`. Then `cd ~/sdc_agent_demo && ./start_agent.sh`.
