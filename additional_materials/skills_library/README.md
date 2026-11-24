# Skill library: 13 research skills to take home

These were written for the workshop but are not used in the session (the session uses one skill, `lesson2_agentic_coding/skills/notebook`). Install the ones you want after the workshop.

## What a skill is

A **skill** is a folder with one file, `SKILL.md`: a short description (when to use it) and instructions (how to do the task, which checks to report, what never to do). It is your method, written down so a coding agent follows it the same way every time.

```
latex-table/
└── SKILL.md       # required. A skill can also hold scripts/, templates or examples next to it
```

```markdown
---
name: latex-table
description: Turn a results file into a LaTeX table ... Use when the researcher asks for a LaTeX table.
---
# Results → LaTeX table
## Ask first      the decisions the agent must leave to you
## Steps          the code skeleton and the order
## Required checks   what every report must show
## Never          the shortcuts that would make the result wrong
```

## How the agent uses them

1. **At startup** the agent reads only the `name` and `description` of every installed skill (a few lines each, so you can have many).
2. **When your request matches a description**, it loads the full `SKILL.md`. You see this in the log, e.g. `[skill] code-texts`.
3. **It follows the instructions**, including the checks.

So the `description` is what decides whether a skill is used: name the task in the words you would type. You can also ask directly: *"use the latex-table skill"*. To see what is installed, ask *"which skills can you use?"*

A skill is a set of instructions, not a lock. What the agent is **allowed** to do is set by its permissions (in this lesson: `opencode.json`).

## Install a skill

Copy the skill's folder to one of these places:

| | This project only | All your projects |
| --- | --- | --- |
| **OpenCode** | `.opencode/skills/` or `.agents/skills/` | `~/.config/opencode/skills/` or `~/.agents/skills/` |
| **Claude Code** | `.claude/skills/` | `~/.claude/skills/` |

OpenCode also reads `.claude/skills/`, so **`.claude/skills/` works for both**. The format is an open standard ([agentskills.io](https://agentskills.io)) that a growing number of agents read.

```bash
mkdir -p ~/.claude/skills && cp -r latex-table edit-paper check-citations ~/.claude/skills/   # for every project
```

Restart the agent after installing. Read a skill before you install it, above all one from someone else: it tells the agent what to do on your computer.

## The skills in this folder

All follow the same pattern: **ask the researcher first, then do the work, then report the checks.**

| Skill | Use it to | From |
| --- | --- | --- |
| **Data and analysis** | | |
| `explore-data` | Take a first look at a new dataset: a data card plus questions about cleaning, without changing the raw file | – |
| `code-texts` | Code texts with an LLM and a codebook: test on 3 rows, quote check, cost | notebook 01 |
| `check-agreement` | Measure agreement between coders: kappa, the confusion table, the disagreements | notebook 02 |
| `cluster-texts` | Group texts by their words (TF-IDF, k-means) and check whether the groups are stable | notebook 03 |
| `search-literature` | Search OpenAlex and save the papers, recording the exact query and date | notebooks 03, 04 |
| `run-regression` | Estimate the model you specified and log every specification tried | – |
| **Writing** | | |
| `make-figure` | Make a figure for a paper or slides: one script, colour-blind safe, PDF and PNG | – |
| `latex-table` | Turn a results file into a LaTeX table, checking it against the source | – |
| `methods-section` | Draft the methods section from the project's own records, with a list of gaps | – |
| `edit-paper` | Edit the prose of a `.tex` file (Overleaf via Git) without changing claims; every change listed | – |
| `check-citations` | Check that every `\cite` exists, DOIs resolve and references are real | – |
| `reply-to-reviewers` | Turn referee reports into a response letter linked to the changes | – |
| **Sharing** | | |
| `replication-package` | Package a project so one command reproduces every table and figure, tested from a clean copy | – |

## Write your own

Start from `lesson2_agentic_coding/SKILL_TEMPLATE.md`. A good skill comes from something you have done by hand at least once, for example a notebook that works. Write down the decisions you made (*Ask first*), the steps, and how you knew the result was right (*Required checks*).
