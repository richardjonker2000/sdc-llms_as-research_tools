---
name: replication-package
description: Prepare a replication package for a paper - folder structure, README, environment file, one script that reproduces every table and figure from the raw data - and test it from a clean copy. Use when the researcher asks to share code and data, prepare for a journal's data editor, archive a project, or make the work reproducible.
---

# Replication package

Test: someone else, with a clean computer, gets the same tables and figures by running one command.

## Ask first (method: the researcher decides)

1. **What may be shared**: data licences, personal data, confidential data. If the data cannot be shared, the package includes the code plus instructions to obtain the data.
2. **Which outputs** must be reproduced (the tables and figures in the paper, by number).
3. The journal's requirements (many economics journals follow the AEA Data Editor template).

## Steps

1. Structure: `data/raw/` (never modified), `data/derived/`, `code/` (numbered scripts), `outputs/`, `README.md`, `requirements.txt` with versions (`pip freeze` of what is actually used), `run_all.sh` (or `run_all.py`).
2. README: data sources with access dates and licences, software and versions, run time, hardware, and a table **output → script** (Table 2 → `code/04_models.py`).
3. LLM steps: include the prompts, the model name and date, and the saved answers (cache), because the live API will not return the same answers later.
4. Test: copy to a new folder, create a fresh environment, run `run_all`, compare every output with the paper's numbers.

## Required in the report

- The clean-copy test: passed or failed, run time, and every output that differs (and by how much).
- Files that are missing, hard-coded paths (`C:\Users\...`, `/home/...`), random steps without a seed.
- What cannot be shared and how the README handles it.

## Never

- include keys, passwords or `config.env` (search the package for `key`, `token`, `password` before finishing);
- include personal data that the researcher has not cleared;
- mark the test passed if any output differs, even slightly: report the difference.
