---
name: make-figure
description: Make a publication-quality figure from a results file - one script, readable at print size, colour-blind safe, saved as PDF and PNG. Use when the researcher asks for a plot, chart, graph or figure for a paper or slides.
---

# Make a figure for a paper or slides

A figure is a claim. It must show the data the text describes, and nothing it doesn't.

## Ask first (method: the researcher decides)

1. **The one message** of the figure, in one sentence ("AI patents shifted towards automation after 2018").
2. **Which data** (file and columns) and which comparison: over time, between groups, a distribution.
3. **Where it goes**: paper (one column ~8.5 cm, two columns ~17 cm) or slides (16:9).

## Steps (one script: `analysis/fig_<name>.py`)

```python
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(3.4, 2.4))                # inches: one column of a paper
...                                                      # one chart type that fits the comparison
ax.set_xlabel("Filing year"); ax.set_ylabel("Share of AI patents (%)")   # units in every label
fig.tight_layout()
fig.savefig("outputs/fig_<name>.pdf"); fig.savefig("outputs/fig_<name>.png", dpi=300)
```

- Bars start at zero. Lines for time. Dots or boxes for distributions. No 3D, no pie charts with more than 3 slices, no two y-axes.
- Colour-blind safe colours (e.g. matplotlib's `tab10` first 4, or Okabe-Ito); never colour alone to tell groups apart if it goes to print: add labels or line styles.
- Label lines directly instead of a legend when there are 4 or fewer.

## Required in the report

- The file paths, the figure's message in one sentence, and N behind each bar/line.
- A draft caption: what is shown, the data source, N, and what error bars mean (if any).
- Anything the figure hides (groups merged, outliers cut off, axis truncated).

## Never

- truncate an axis or change the scale to make a difference look bigger;
- smooth, drop or aggregate data without saying so in the caption;
- invent numbers: every value comes from the results file.
