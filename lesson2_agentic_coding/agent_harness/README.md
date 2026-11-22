# Agent harness: a coding agent that owns the code, while the researcher owns the method

A starter project for the "inverse" session. A social-science researcher with little coding experience works with a coding agent ([OpenCode](https://opencode.ai)) on a real dataset: 151 USPTO patents, plus notebook 01's LLM codes for 100 of them and the codebook that made them.

- **The agent** fixes code problems on its own: environments, encodings, bugs, plots.
- **The researcher** decides every methodological choice: sample, definitions, codebook, LLM use, statistics.

There is no sandbox. The control comes from OpenCode's own permissions and instructions:

| File | What it does |
| --- | --- |
| `AGENTS.md` | Roles, the code-vs-method split, the workflow, the `PLAN.md` template, the step report format, hard rules |
| `opencode.json` | Permissions: no web, no edits outside the agent's own folders, a bash allowlist; `git config`, `rm`, `curl`, `sudo` and reading `config.env` are denied |
| `.opencode/agents/planner.md` | Writes only `PLAN.md` (plus a data-inspection script); ends each turn with numbered decisions D1, D2, ... |
| `.opencode/agents/builder.md` | Does exactly one plan step, reports, and stops |
| `.opencode/commands/` | `/plan <idea>`, `/revise <answers>`, `/next`, `/extra <job>` (LaTeX table, diagram), `/explain`, `/status` |
| `.opencode/skills/code-texts/`, `check-agreement/`, `cluster-texts/` | The methods of lesson 1 notebooks 01, 02 and 03 as skills: what to ask the researcher, the steps, the required checks |
| `.opencode/skills/setup-env/` | Environment troubleshooting for student laptops in China and Denmark |
| `data/codebook.py` | Notebook 01's codebook, word for word: the agent imports it and may not change it |
| `tools/check_env.py` | Read-only environment check; writes `outputs/ENVIRONMENT.txt` |
| `workshop/` | The same LLM helper as the notebooks; `DRY_RUN=1` gives fake answers |

## The loop

1. `/plan My research idea ...` → `PLAN.md` with open decisions.
2. `/revise D1: a, D2: ...` → repeat until happy.
3. `/next` → one step, a short report ("Please check: ..."), and a git commit. Repeat.

## Run it

Easiest: from the repo root run `./setup.sh`. It builds `~/sdc_agent_demo` with all of the below; then `cd ~/sdc_agent_demo && ./start_agent.sh`. By hand:

```bash
cd lesson2_agentic_coding/agent_harness
python -m venv .venv && .venv/bin/python -m pip install -r requirements.txt
cp ../config.example.env config.env      # then set DRY_RUN=1 (fake answers) until the researcher goes live
git init && git config user.name "Researcher (workshop)" && git config user.email researcher@workshop.local
git add -A && git commit -m "Starter"
export MINIMAX_API_KEY=...               # the workshop key, never a personal one
opencode                                 # interactive; or: opencode run --command plan "..."
```

**Workshop demo:** the run sheet, the prepared run (one git tag per turn) and its transcripts are in `../demo/`, outside this folder so the agent never sees them. `../demo/show_turn.py` turns an `opencode run --format json` log into a readable transcript.

China-specific setup and open issues: see `../../docs/DEPLOYMENT_CHINA.md`, section 5.
