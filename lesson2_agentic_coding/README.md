# Lesson 2 · Agentic coding and skill files (14:00–15:00)

In lesson 1 you ran each step yourself in a notebook. Here a coding agent writes and runs the code, while you make every method decision. A **skill file** is the bridge: your method written down as instructions the agent must follow, checks included.

| | What it is |
| --- | --- |
| `skills/notebook/` | **One skill**: how an agent shows, changes and runs a notebook cell by cell, checks the output, and reports. `nb.py` is the small helper it uses |
| `agent_harness/` | The project the agent works in ([OpenCode](https://opencode.ai)): the lesson 1 notebooks, the rules (`AGENTS.md`) and the permissions (`opencode.json`) |
| `SKILL_TEMPLATE.md` | Write your own skill |

More skills to take home (coding texts, agreement, figures, LaTeX tables, methods sections, replication packages) are in `additional_materials/skills_library/`.

Quick start: `./setup.sh` builds `~/sdc_agent_demo`; `./start_agent.sh` there, then e.g. *"in notebook 01, add a field is_medical to the codebook and run it"*.
