---
name: explore-data
description: First look at a new dataset (CSV, Excel, Stata, survey export) before any analysis. Use when the researcher hands over a data file, asks "what is in this data", or before the first analysis step. Writes a data card - rows, columns, types, missing values, duplicates, odd values - and never changes the raw file.
---

# First look at a dataset

The researcher knows what the data *should* contain; the data card shows what it *does* contain. Nothing is cleaned yet: cleaning rules are method decisions.

## Ask first (method: the researcher decides)

1. **Which file**, and what one row is meant to be (a person, a firm-year, a patent, a document).
2. **The key**: which column(s) should identify a row uniquely.
3. Anything already known to be wrong or special (codes like `-99` or `999` for missing, a changed survey question).

## Steps (one script: `analysis/s1_explore.py`)

```python
import pandas as pd
df = pd.read_csv(PATH)                                   # or read_excel / read_stata: never write back to PATH
print(df.shape); print(df.dtypes)
print(df.isna().sum().sort_values(ascending=False))      # missing per column
print(df.duplicated(subset=KEY).sum(), "duplicate keys")
print(df.describe(include="all").T)                      # ranges, most common values
for col in df.select_dtypes("object"):
    print(col, df[col].nunique(), df[col].value_counts().head(5).to_dict())
```

## Required in the report (`outputs/data_card.md`)

- Rows and columns; what one row is; whether the key is unique (and the duplicate count if not).
- Per column: type, % missing, range or top values.
- **Suspicious things**, each with the row count: impossible values (age 200, year 1900), codes that look like missing (`-99`, `999`, `"n/a"`), text in number columns, inconsistent spellings of the same category, dates in mixed formats.
- A list of **cleaning questions** for the researcher (e.g. "Treat -99 as missing? 312 rows"). Do not answer them yourself.

## Never

- modify, overwrite or "fix" the raw file: cleaning happens in a later script that writes a new file;
- drop rows or impute values in this step;
- guess what a code means and present the guess as fact.
