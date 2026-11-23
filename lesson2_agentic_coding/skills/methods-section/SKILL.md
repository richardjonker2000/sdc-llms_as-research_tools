---
name: methods-section
description: Draft the methods (data and methods) section of a paper from the project's own records - the plan, the scripts, the git log, the skill files and the outputs - so every sentence can be traced to what was actually done. Use when the researcher asks to write up the methods, the data section, a methods appendix, or to describe the LLM use for a paper.
---

# Draft the methods section from the record

A methods section describes what was done, not what should have been done. Everything comes from the project's files; nothing is filled in from general knowledge.

## Ask first (method: the researcher decides)

1. **The venue and length** (journal section, appendix, thesis chapter; word limit).
2. **What to include about LLM use**: model and version, date, prompts (in full in an appendix?), cost, validation.
3. Citation style, and which methods references the researcher wants cited (do not pick references yourself).

## Steps

1. Read `PLAN.md`, `git log --oneline`, the scripts in `analysis/`, the skill files used, and the report files in `outputs/`.
2. Write `outputs/methods_draft.md` with these parts: data (source, date, sample and how it was drawn, N at each step), measures (the codebook or variables, with definitions), procedure (each step in order), validation (agreement, quote checks, robustness), and LLM use (model, date, temperature, prompt location, cost).
3. After each paragraph, a comment with its sources: `<!-- PLAN.md D1; analysis/s2_code.py; outputs/s2_report.txt -->`.

## Required in the report

- A list of **gaps**: things a reviewer will ask that the record does not answer (e.g. "why 100 patents?", "who chose the seed?"). The researcher fills them in.
- Every number in the draft with the file it came from (as in `CLAIMS.md`, if the project has one).

## Never

- invent a justification for a choice the record does not explain: list it as a gap;
- describe a check as done unless an output file shows it was done;
- call LLM-vs-LLM agreement "validation", or LLM codes "human" codes;
- add citations the researcher did not provide.
