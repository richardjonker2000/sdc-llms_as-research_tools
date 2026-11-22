# Lesson 2 · Agentic coding and skill files (14:00–15:00)

Lesson 1 ran each step yourself in a notebook. Here a coding agent writes and runs the code, while you make every method decision. A **skill file** is the bridge: your notebook's method written down as instructions the agent must follow, checks included.

| | What it is |
| --- | --- |
| `agent_harness/` | A starter research project for a coding agent ([OpenCode](https://opencode.ai)): the rules (`AGENTS.md`), the permissions (`opencode.json`), commands (`/plan`, `/revise`, `/next`, `/extra`, `/explain`), the data and the codebook from notebook 01, and the skills. |
| `agent_harness/.opencode/skills/` | Three skills, one per lesson 1 notebook: **`code-texts`** (01: LLM coding with a codebook), **`check-agreement`** (02: agreement between coders), **`cluster-texts`** (03: grouping texts without labels). Plus `setup-env` for environment trouble. |
| `SKILL_TEMPLATE.md` | Write your own skill: what to ask the researcher, the steps, the required checks, what never to do. |
| `demo/` | Organisers: the run sheet (`DEMO.md`), the prepared run (one git tag per turn) and the transcripts. Kept outside `agent_harness/` so the agent never sees them. |

Try it: `./setup.sh` in the main folder builds a ready copy in `~/sdc_agent_demo`; then `cd ~/sdc_agent_demo && ./start_agent.sh`. The skills also work in Claude Code: copy a skill folder to `.claude/skills/`.
