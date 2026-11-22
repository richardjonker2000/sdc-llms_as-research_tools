---
name: check-agreement
description: Measure agreement between two coders of the same items (a human and the LLM, two LLM runs, or two models), the method of lesson 1 notebook 02. Use whenever a plan step validates codes, compares coders, or reports reliability. Gives percent agreement, Cohen's kappa, weighted kappa for ordered labels, the confusion table and the disagreements.
---

# Check agreement between coders

Same method as **lesson 1, notebook 02**. Agreement is how we know whether codes can be trusted, so the numbers and the disagreements always go to the researcher.

## Ask first (method: the researcher decides)

1. **Which coders** are compared (human vs LLM is the strongest check; two runs of one model is only the floor).
2. **Which items**: all coded items, or the hand-coded sample. A hand-coded sample comes from the researcher; never create or fill in "human" codes yourself.
3. **Ordered or not**: are the categories ordered (low < medium < high)? Then report weighted kappa too.

## Steps (one script: `analysis/sN_agreement_<what>.py`)

```python
import numpy as np
import pandas as pd

def percent_agreement(x, y):
    return (x == y).mean()

def cohen_kappa(x, y, levels):
    p_o = (x == y).mean()                                                   # observed agreement
    p_e = sum((x == lvl).mean() * (y == lvl).mean() for lvl in levels)     # agreement by chance
    return (p_o - p_e) / (1 - p_e)

def weighted_kappa(x, y, levels):                                          # only for ordered levels
    k, pos = len(levels), {lvl: i for i, lvl in enumerate(levels)}
    observed = np.zeros((k, k))
    for a, b in zip(x, y):
        observed[pos[a], pos[b]] += 1
    observed /= observed.sum()
    expected = np.outer(observed.sum(axis=1), observed.sum(axis=0))
    distance = np.abs(np.subtract.outer(range(k), range(k))) / (k - 1)
    return 1 - (distance * observed).sum() / (distance * expected).sum()

both = ...                       # one row per item, columns: id, coder_1, coder_2 (drop rows missing either code, report how many)
levels = [...]                   # all categories, in order if they are ordered
print(pd.crosstab(both.coder_1, both.coder_2, margins=True))
```

## Required in the report

- **N**: how many items, and how many were dropped because a code was missing.
- **Percent agreement and Cohen's kappa** (plus weighted kappa if ordered), printed by the script, with 2 decimals.
- **The confusion table**, and whether one coder uses a category much more often than the other (row totals vs column totals): that is a systematic difference, not noise.
- **The disagreements**: save them to `outputs/<name>_disagreements.csv` (id, text, both codes, any reasons) and tell the researcher to read them. They show where the codebook is unclear.
- A rough guide for kappa, labelled as a guide: below 0.2 slight, 0.2-0.4 fair, 0.4-0.6 moderate, 0.6-0.8 substantial, above 0.8 almost perfect (Landis & Koch, 1977).

## Never

- call LLM codes "human" codes, or an LLM-vs-LLM comparison "validation";
- drop disagreements, or re-code until agreement improves;
- judge whether the agreement is "good enough" for the study: that is the researcher's call.
