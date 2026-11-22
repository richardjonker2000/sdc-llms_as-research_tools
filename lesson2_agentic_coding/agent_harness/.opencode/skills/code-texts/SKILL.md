---
name: code-texts
description: Code texts (abstracts, interview answers, reports) into variables with an LLM and a written codebook, the method of lesson 1 notebook 01. Use whenever a plan step says to code, classify or extract information from text with the LLM. Covers the codebook, the test run, the full run, and the checks every run must report.
---

# Code texts with an LLM and a codebook

Same method as **lesson 1, notebook 01**: a codebook (a pydantic class) and the text go to the LLM; every answer is validated against the codebook; the evidence quote is checked against the text.

## Ask first (method: the researcher decides)

Do not start until the plan records these. If one is open, stop and ask.

1. **The codebook.** If the researcher has one (here: `data/codebook.py`, notebook 01's codebook), import it and **never edit it**. Changing a definition or a category is a method decision. If there is none, draft one in `PLAN.md` as a table (variable, type, allowed values, instruction) and ask for approval before coding anything.
2. **Which rows**, and why those rows (all, a random sample with a seed, only the not-yet-coded ones).
3. **Live or saved answers.** `config.env` has `DRY_RUN=1`: saved answers replay, anything new is FAKE. Only the researcher switches live calls on, and should know the expected cost first (step 4 below gives it).

## Steps (one script: `analysis/sN_code_<what>.py`)

```python
import sys
sys.path.insert(0, ".")          # the workshop helpers
sys.path.insert(0, "data")       # the researcher's codebook
import pandas as pd
from workshop import extract_many, quote_check, usage_table, cost, CFG
from codebook import PatentCode, INSTRUCTIONS   # import, never edit

rows = ...                                         # exactly the rows the plan says, e.g. patents not yet coded
test = extract_many(rows.head(3), "abstract", PatentCode, INSTRUCTIONS)
print(test.drop(columns=["abstract"], errors="ignore").to_string())   # 1. test on 3 rows, read the answers

coded = extract_many(rows, "abstract", PatentCode, INSTRUCTIONS)       # 2. all rows
coded["quote_ok"] = [quote_check(q, t) for q, t in zip(coded.evidence_quote.fillna(""), rows.abstract)]
```

1. **Test on 3 rows** and look at the answers before the full run. If they look wrong, stop and report: the codebook may need the researcher.
2. **Run all rows** in the same script only if the plan step says so.
3. **Save** the result (`outputs/<name>.csv`, without the long text column) and commit.

## Required checks (always in the report, from what the script printed)

| Check | Code | What to report |
| --- | --- | --- |
| Failed rows | `coded.error.notna().sum()` | how many, and why (first error message) |
| Real or fake | `coded._source.value_counts()` | live / cache / fake. **Any fake answer: the results are not real.** Say so first and do not report them as findings |
| Quote check | `(~coded.quote_ok).sum()` | how many evidence quotes are not in the text, and list their ids |
| Value counts | `coded[<field>].value_counts()` | for every closed category |
| Cost | `cost(usage_table().to_dict("records"))`, `CFG["currency"]` | the cost of the run at the live price, tokens in and out, and what 10,000 texts would cost |

## Never

- change the codebook, the instructions or the prompt to "improve" results;
- drop, recode or merge categories, or drop rows that failed or have a bad quote (report them instead);
- re-run until the numbers look better;
- describe fake answers as results.
