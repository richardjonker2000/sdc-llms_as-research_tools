---
name: setup-env
description: Diagnose and fix Python environment problems on students' laptops (Windows/macOS, in China or Denmark) - wrong interpreter or Jupyter kernel, ModuleNotFoundError, pip timeouts behind the Great Firewall, Chinese characters showing as boxes in plots, UnicodeDecodeError on CSVs, scripts that only run from one folder. Use before the first analysis script and whenever code fails for a reason that is not the analysis itself.
---

# Environment: diagnose, propose, record

The researcher owns the environment. You diagnose and propose exact commands; the researcher runs or approves them. Never install silently.

## 1. Run the checker first

```
.venv/bin/python tools/check_env.py          # macOS / Linux
.venv\Scripts\python.exe tools\check_env.py   # Windows
```

It checks the interpreter, the pinned packages, a font that can draw Chinese, and that the project path has no spaces/non-ASCII characters that break some tools. On `ENV OK` it writes `outputs/ENVIRONMENT.txt`; commit it. On `ENV PROBLEM`, use the table below.

## 2. Symptom -> cause -> fix

| Symptom | Usual cause | What to propose |
| --- | --- | --- |
| `ModuleNotFoundError` but "I installed it" | Code runs with a different Python than the one pip installed into (system Python, Anaconda base, wrong Jupyter kernel) | Print `sys.executable` in the failing place. In VS Code/Jupyter pick the `.venv` kernel. Install with the venv's own Python: `.venv/bin/python -m pip install ...`, never bare `pip` |
| `pip install` hangs or times out (in China) | PyPI is slow or blocked | Use a mirror: `uv pip install --python .venv/bin/python -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple` (alternative: `https://mirrors.aliyun.com/pypi/simple/`) |
| `No module named ...` for a package not in `requirements.txt` | You (the agent) used a package the project does not have | First try the standard library / pandas / networkx. If really needed: write in `NEEDS.md` which package, pinned version, why, and the install command. After the researcher installs it, add the pinned line to `requirements.txt` |
| Chinese text shows as empty boxes in a figure | matplotlib's default font has no CJK glyphs | Use the font the checker found: `plt.rcParams["font.sans-serif"] = [<that font>, "DejaVu Sans"]`. Do not download fonts |
| `UnicodeDecodeError` / garbled Chinese when reading or writing CSV | Windows default encoding is not UTF-8 | Always pass `encoding="utf-8"` to `read_csv`, `to_csv`, `open()`, `write_text()`. For files that Excel will open, write with `encoding="utf-8-sig"` |
| `FileNotFoundError` for `data/...` when run from another folder | Paths relative to the current directory | In every script: `ROOT = Path(__file__).resolve().parent.parent` and build paths from `ROOT`. Never hard-code `C:\Users\...` or `/home/...` |
| Script hangs or errors with "no display" / Tk errors | Interactive plotting backend in a script | Scripts save figures; start them with `import matplotlib; matplotlib.use("Agg")` |
| Results change between runs | Unseeded randomness (sampling, Louvain, layouts) | Set seeds (`random_state=1`, `seed=1`) and note them in `CLAIMS.md` |
| Different numbers on another laptop | Package versions differ | Compare `outputs/ENVIRONMENT.txt` from both machines; install the versions pinned in `requirements.txt` |

## 3. Rules

- Run Python only as `.venv/bin/python` (Windows: `.venv\Scripts\python.exe`).
- Do not create new virtual environments, use `conda`, `sudo`, or edit `requirements.txt` without the researcher's OK.
- When you finish, re-run the checker; if `outputs/ENVIRONMENT.txt` changed (`git diff`), say so.
