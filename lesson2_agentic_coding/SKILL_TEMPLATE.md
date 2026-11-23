---
name: <short-name-with-dashes>
description: <One or two sentences: what this skill does and WHEN the agent should use it. The agent reads only this line to decide, so name the task in the words a researcher would use.>
---

# <What the skill does, in plain words>

<One line: which notebook or method this comes from, e.g. "Same method as lesson 1, notebook 01".>

## Ask first (method: the researcher decides)

<The decisions the agent must never make on its own. Examples:>

1. <The codebook / categories / keyword list: where it is, and that the agent must not change it.>
2. <Which rows or cases, and why.>
3. <Live API calls and the budget.>

## Steps (one script: `analysis/sN_<what>.py`)

```python
# The skeleton the agent should follow: the imports, the key function calls, the order.
# Copy the important cells from your notebook here.
```

1. <Test on a few cases first; read the result.>
2. <Run all.>
3. <Save the output and commit.>

## Required checks (always in the report)

| Check | Code | What to report |
| --- | --- | --- |
| <e.g. failed rows> | `<code>` | <what the researcher needs to see> |
| <e.g. quote check> | `<code>` | <...> |
| <e.g. cost> | `<code>` | <...> |

## Never

- <the shortcuts that would make the results invalid: changing the codebook, dropping awkward rows, re-running until it looks better, ...>

---
*How to use it:* save this file as `.claude/skills/<short-name>/SKILL.md` in your project (read by Claude Code and OpenCode); see `skills/README.md` for the other places. The agent finds it by the `description` line. The skills in `skills/` are worked examples.
