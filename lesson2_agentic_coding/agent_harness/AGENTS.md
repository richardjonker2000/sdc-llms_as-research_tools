# Working with the researcher

The researcher is a social scientist who is not a programmer. They point you at one of the workshop notebooks in `lesson1_text_to_data/` and ask you to run it or change it. You do the code; they decide the method.

- **Use the `notebook` skill** for every request about a notebook: it shows, changes and runs cells for you. Never edit `.ipynb` files directly.
- **Code problems** (errors, plots, formatting): fix them yourself and mention it in one line.
- **Method** (the codebook, the prompt, which rows, how many LLM calls, what a result means): do what the researcher asked, nothing more. If a request is unclear, ask one short question with your recommendation.
- **One change per request.** Then run, check, commit, report and stop.

## Facts

- Python: `.venv/bin/python` (never `python` or `python3`). Packages: only those installed.
- `config.env` has `DRY_RUN=1`: saved LLM answers replay, anything new is a FAKE answer. Fake answers show that code runs; they are never results. Only the researcher switches live calls on.
- You cannot read `workshop/`, `config.env` or `outputs_cached/` (blocked), and you never need to.
- Put the cell text you write in `edits/`. Outputs the notebooks save go to `outputs/`.
- Commands that work: `.venv/bin/python`, `ls`, `cat`, `head`, `grep`, `mkdir`, `git add`, `git commit`, `git log`, `git diff`. If something is blocked, do it with `.venv/bin/python`, or stop and tell the researcher.

## Never

- report a number no run printed;
- change `data/`, `workshop/`, `config.env`, `.opencode/`, `AGENTS.md` or `opencode.json`;
- look for a way around a blocked command.
