---
name: edit-paper
description: Edit academic prose in LaTeX (.tex) or Markdown files - clearer, shorter, consistent terms - without changing claims, numbers, citations or meaning, and with every change listed for the researcher to accept or reject. Use when the researcher asks to proofread, tighten, polish, shorten or fix the language of a paper, including an Overleaf project synced to a local folder.
---

# Edit a paper without changing what it says

The researcher owns the argument. The agent improves the sentences and shows every change.

## Ask first (method: the researcher decides)

1. **Which file and section**, and the goal: proofread only, tighten, shorten to N words, or make consistent.
2. **The language variety** (British or American English) and any terms that must stay exactly as they are.
3. **How to deliver**: edit in place on a git branch (best: the researcher sees a diff), or a separate copy.

## Working with Overleaf

The agent works on local files. Overleaf projects can be synced with **Git** (Overleaf menu → *Git*, or *GitHub sync*; paid plans) - then `git pull`, edit, commit, `git push`, and the researcher reviews the changes in Overleaf's history. Without that: download the project as a zip, edit, and upload the changed `.tex` files.

## Steps

1. `git switch -c edit/<section>` (so the original stays untouched).
2. Edit the prose only. Leave untouched: everything inside `$...$`, `\cite{}`, `\ref{}`, `\label{}`, figures, tables, numbers, and quoted material.
3. Check the file still compiles (`latexmk -pdf` if installed) and commit.
4. Write `outputs/edit_<section>.md`: a table of changes (old → new, reason), longest first.

## Required in the report

- Words before and after.
- Any sentence where you were unsure whether a change alters the meaning: list it, do not change it.
- Claims that look unsupported or inconsistent with another section: list them as questions, do not fix them.

## Never

- change a number, a hedge ("may", "suggests") into a stronger claim, or a citation;
- add new content, examples or references;
- rewrite the whole text in one commit without a list of changes.
