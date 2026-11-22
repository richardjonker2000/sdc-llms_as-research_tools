"""Build lesson1_text_to_data/*.ipynb from tools/nb_src/*.txt (cells separated by '%% md' / '%% code' lines).

Usage: python tools/build_notebooks.py [02 03 ...]   (no arguments: build all)
Organisers can edit the .ipynb files directly; this script is only a convenience for bulk edits.
"""
import sys
from pathlib import Path

import nbformat

SRC = Path(__file__).parent / "nb_src"
OUT = Path(__file__).resolve().parent.parent / "lesson1_text_to_data"

# optional: names to build, e.g. python tools/build_notebooks.py 02 03 (default: all)
for src in sorted(p for p in SRC.glob("*.txt") if not sys.argv[1:] or any(p.stem.startswith(a) for a in sys.argv[1:])):
    nb = nbformat.v4.new_notebook()
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    for chunk in ("\n" + src.read_text(encoding="utf-8")).split("\n%% ")[1:]:
        kind, _, body = chunk.partition("\n")
        make = nbformat.v4.new_markdown_cell if kind.strip() == "md" else nbformat.v4.new_code_cell
        nb.cells.append(make(body.strip("\n")))
    nbformat.write(nb, OUT / f"{src.stem}.ipynb")
    print("built", src.stem, len(nb.cells), "cells")
