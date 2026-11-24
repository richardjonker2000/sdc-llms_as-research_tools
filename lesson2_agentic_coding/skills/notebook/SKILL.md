---
name: notebook
description: Run a Jupyter notebook and make a change to it that the researcher asks for (a new codebook field, another sample size, a different figure, a fix). Use whenever the researcher names a notebook (.ipynb) or asks to run, change, extend or explain one.
---

# Run and change a notebook

The notebooks are in `lesson1_text_to_data/`. Never edit their JSON by hand: use the helper, which shows, replaces and runs cells.

```
NB=".venv/bin/python .opencode/skills/notebook/nb.py"
$NB show lesson1_text_to_data/01_codebook_extraction.ipynb      # list the cells
$NB cell lesson1_text_to_data/01_codebook_extraction.ipynb 12   # read one cell in full
$NB set  lesson1_text_to_data/01_codebook_extraction.ipynb 12 edits/cell12.py   # replace a cell
$NB add  lesson1_text_to_data/01_codebook_extraction.ipynb 12 edits/new.py      # new cell after 12 (add md for text)
$NB run  lesson1_text_to_data/01_codebook_extraction.ipynb      # run all, outputs saved in the notebook
```

## Steps

1. **Look.** `show` the notebook, then `cell` the cells the request is about. Say in 2 lines which cells you will change.
2. **Change only what was asked.** Write the new cell text to `edits/cellN.py` (or `.md`), then `set` (or `add`). Keep everything else as it is. If the request is unclear, or would change the method in a way the researcher did not ask for (the codebook, the prompt, which rows), ask first.
3. **Run** the whole notebook with `run`. If it stops at an error in code you wrote, fix it and run again (at most 3 tries, then report).
4. **Check** in the printed output: no errors; the cost line under each LLM cell; whether answers were `live`, `cache` or `fake`.
5. **Commit:** `git add lesson1_text_to_data edits` then `git commit -m "<notebook>: <what changed>"`.
6. **Report** in this form, then stop:

```
**Changed:** <notebook>, cell N: <what, in plain words>
**Result:** <the key numbers or table the run printed>
**Real or fake:** <live / cache / fake. Fake answers are not results: say so first>
**Cost:** <from the cost lines>
**Open it:** <notebook> in Jupyter, cell N
```

## Never

- report a number the run did not print;
- present fake answers (dry run) as findings;
- change `config.env`, `workshop/` or `data/`, or switch dry run off: only the researcher does that.
