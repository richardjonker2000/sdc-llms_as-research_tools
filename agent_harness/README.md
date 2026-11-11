# Agent harness: a coding agent that owns the code, while the researcher owns the method

A starter project for the "inverse" session. A social-science researcher with little coding experience works with a coding agent ([OpenCode](https://opencode.ai)) on a real dataset: 151 USPTO patents, plus notebook 01's LLM codes for 30 of them.

- **The agent** fixes code problems on its own: environments, encodings, bugs, plots.
- **The researcher** decides every methodological choice: sample, definitions, codebook, LLM use, statistics.

There is no sandbox. The control comes from OpenCode's own permissions and instructions:

| File | What it does |
| --- | --- |
| `AGENTS.md` | Roles, the code-vs-method split, the workflow, the `PLAN.md` template, the step report format, hard rules |
| `opencode.json` | Permissions: no web, no edits outside the agent's own folders, a bash allowlist; `git config`, `rm`, `curl`, `sudo` and reading `config.env` are denied |
| `.opencode/agents/planner.md` | Writes only `PLAN.md` (plus a data-inspection script); ends each turn with numbered decisions D1, D2, ... |
| `.opencode/agents/builder.md` | Does exactly one plan step, reports, and stops |
| `.opencode/commands/` | `/plan <idea>`, `/revise <answers>`, `/next`, `/explain`, `/status` |
| `.opencode/skills/setup-env/` | Environment troubleshooting for student laptops in China and Denmark |
| `tools/check_env.py` | Read-only environment check; writes `outputs/ENVIRONMENT.txt` |
| `workshop/` | The same LLM helper as the notebooks; `DRY_RUN=1` gives fake answers |

## The loop

1. `/plan My research idea ...` → `PLAN.md` with open decisions.
2. `/revise D1: a, D2: ...` → repeat until happy.
3. `/next` → one step, a short report ("Please check: ..."), and a git commit. Repeat.

## Run it

```bash
cd agent_harness
python -m venv .venv && .venv/bin/python -m pip install -r requirements.txt
cp ../config.example.env config.env      # then set DRY_RUN=1 (fake answers) until the researcher goes live
git init && git config user.name "Researcher (workshop)" && git config user.email researcher@workshop.local
git add -A && git commit -m "Starter"
export MINIMAX_API_KEY=...               # the workshop key, never a personal one
opencode                                 # interactive; or: opencode run --command plan "..."
```

`tools_facilitator_show_turn.py` turns an `opencode run --format json` log into a readable transcript.

China-specific setup and open issues: see `../docs/DEPLOYMENT_CHINA.md`, section 5.
