# Agent harness: point a coding agent at a notebook

A small project for a coding agent ([OpenCode](https://opencode.ai)): the lesson 1 notebooks, one skill, and rules. You point the agent at a notebook and ask for a change in plain words; it changes the cell, runs the notebook, checks the output, commits, and reports.

| File | What it does |
| --- | --- |
| `AGENTS.md` | The rules: the agent does the code, you decide the method; one change per request; fake answers are never results |
| `opencode.json` | Permissions: no web, edits only in `edits/` and `outputs/`, a short list of allowed commands; `config.env`, `workshop/` and the saved answers are blocked |
| `.opencode/skills/notebook/` | The one skill: how to show, change and run a notebook, check it, and report (filled by `setup.sh` from `../skills/`) |

## Try

```
in notebook 01, add a field is_medical to the codebook and run it
in notebook 03, try 4 groups instead of 6 and tell me what changed
in notebook 02, explain the kappa cell in plain words
```

Then open the notebook in Jupyter: the changed cell and its new output are there, and `git log` shows each change.

## Run it

From the main folder: `./setup.sh`. It copies this folder to `~/sdc_agent_demo` together with `lesson1_text_to_data/`, `workshop/`, `data/` and the skill, makes it a git project with its own `.venv` and `DRY_RUN=1`, and writes `start_agent.sh`. Then `cd ~/sdc_agent_demo && ./start_agent.sh`.
