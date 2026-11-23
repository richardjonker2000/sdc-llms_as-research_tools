---
name: reply-to-reviewers
description: Turn referee reports into a response letter - each comment numbered, quoted, answered, and linked to the exact change in the manuscript. Use when the researcher has reviewer comments, a revise-and-resubmit, or asks for a response letter or rebuttal.
---

# Response to reviewers

The researcher decides what to change and what to push back on. The agent organises, drafts and tracks.

## Ask first (method: the researcher decides)

1. **The reports** (files) and the editor's letter.
2. For each comment, the decision: **change** (what?), **partly**, or **disagree** (why?). Draft a proposed decision per comment in a table for the researcher to fill in; do not decide.
3. Tone and length (the field's custom; first person plural or singular).

## Steps

1. Split each report into numbered comments (R1.1, R1.2, R2.1, ...) in `outputs/review_comments.csv`: id, quote, type (major / minor / typo), proposed decision, where in the paper.
2. After the researcher fills in the decisions, draft `outputs/response_letter.md`: per comment, the quote (in italics), the answer, and **"Changes: Section X, page Y"** with the new text quoted.
3. If the manuscript is in git: one commit per comment or group (`R1.3: add robustness check`), so each answer points to a diff.

## Required in the report

- Comments with no decision yet, and comments answered without a change in the manuscript.
- Promises in the letter that are not yet in the manuscript ("we now report ...": is it there?).

## Never

- claim a change was made that is not in the manuscript;
- invent analyses, results or references to satisfy a reviewer;
- drop or merge comments to make the letter shorter;
- write anything dismissive about a reviewer.
