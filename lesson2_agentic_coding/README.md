# Lesson 2 · Agentic coding and skill files (14:00–15:00)

Lesson 1 ran each step yourself in a notebook. Here a coding agent writes and runs the code, while you make every method decision.

| Folder | What it is |
| --- | --- |
| `agent_harness/` | A starter project for a coding agent ([OpenCode](https://opencode.ai)): the rules file (`AGENTS.md`), the permissions (`opencode.json`), commands (`/plan`, `/revise`, `/next`, `/extra`) and skills (`.opencode/skills/`). See its README. |
| `demo/` | Organisers: the run sheet (`DEMO.md`), the prepared run (one git tag per turn) and the transcripts. Kept outside `agent_harness/` so the agent never sees them. |

Try it: `./setup.sh` in the main folder builds a ready copy in `~/sdc_agent_demo`; then `cd ~/sdc_agent_demo && ./start_agent.sh`.
