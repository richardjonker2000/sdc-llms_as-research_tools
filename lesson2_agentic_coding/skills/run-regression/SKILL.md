---
name: run-regression
description: Estimate a regression (OLS, logit, fixed effects) that the researcher has specified, and report it honestly - N, standard errors, the full table, and every specification tried. Use when a plan step says to estimate, regress, test an association or run a model. Choosing the model is the researcher's job, not the agent's.
---

# Run a regression the researcher specified

The specification is a method decision. The agent writes the code, runs it, and reports everything, including the runs that "didn't work".

## Ask first (method: the researcher decides)

1. **The model**: outcome, main variable(s), controls, fixed effects, sample restrictions. Write it as one equation in `PLAN.md` before running.
2. **Standard errors**: robust, clustered (by what?), or default.
3. **What counts as the main result**, decided before seeing it. Robustness checks are listed in advance too.

## Steps (one script per model: `analysis/sN_model_<what>.py`)

```python
import statsmodels.formula.api as smf
m = smf.ols("y ~ x + control1 + C(year)", data=df).fit(cov_type="cluster", cov_kwds={"groups": df["firm"]})
print(m.summary())
print("N used:", int(m.nobs), "of", len(df), "rows")      # rows dropped for missing values
```

Save the table (`outputs/model_<what>.csv`, coefficient, SE, p, N) and append one line to `outputs/models_log.md` for **every** model run: date, formula, SEs, N, main coefficient.

## Required in the report

- The formula exactly as run, the SE type, N used and how many rows were dropped (and why).
- The main coefficient with its standard error and confidence interval, in words a reader understands ("one more X is associated with ... more Y").
- **All specifications run so far** (from `models_log.md`), not only the preferred one.
- Warnings: perfect separation, singular matrix, tiny groups, a coefficient that flips sign across specifications.

## Never

- add or drop controls, change the sample or the SEs until the result is significant;
- report only the specifications that support the hypothesis;
- write "causes" or "effect" when the design only shows an association; flag it instead.
