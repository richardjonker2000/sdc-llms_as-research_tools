# Lesson 2 · Agentic coding and skill files (14:00–15:00)

In lesson 1 you ran each step yourself in a notebook. Here a coding agent writes and runs the code, while you make every method decision. A **skill file** is the bridge: your method written down as instructions the agent must follow, checks included.

| | What it is |
| --- | --- |
| `skills/` | **A skill library to take home**: 13 skills for data and analysis (incl. lesson 1's three methods), writing (figures, LaTeX tables, methods section, editing, citations, reviewers) and sharing (replication package). `skills/README.md` explains what a skill is, how agents load it, and how to install it |
| `SKILL_TEMPLATE.md` | Write your own skill: what to ask the researcher, the steps, the required checks, what never to do |
| `agent_harness/` | The starter research project used in the demo ([OpenCode](https://opencode.ai)): rules, permissions, commands, notebook 01's codebook and codes |

Quick start: copy the skills you want to `~/.claude/skills/` (works for Claude Code and OpenCode), restart the agent, and ask *"which skills can you use?"*
