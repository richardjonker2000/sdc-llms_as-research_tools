# Lesson 2 · Agentic coding and skill files (14:00–15:00)

In lesson 1 you ran each step yourself in a notebook. Here a coding agent writes and runs the code, while you make every method decision. A **skill file** is the bridge: your notebook's method written down as instructions the agent must follow, checks included.

| | What it is |
| --- | --- |
| `agent_harness/` | A starter research project for a coding agent ([OpenCode](https://opencode.ai)): rules, permissions, commands, notebook 01's codebook and codes |
| `agent_harness/.opencode/skills/` | Three skills, one per lesson 1 notebook: **`code-texts`** (01), **`check-agreement`** (02), **`cluster-texts`** (03) |
| `SKILL_TEMPLATE.md` | Write your own skill: what to ask the researcher, the steps, the required checks, what never to do |

The skills also work in Claude Code: copy a skill folder to `.claude/skills/`.
