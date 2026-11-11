"""Build notebooks/*.ipynb from tools/nb_src/*.txt (cells separated by '%% md' / '%% code' lines).

Organisers can edit the .ipynb files directly; this script is only a convenience for bulk edits.
"""
from pathlib import Path

import nbformat

SRC = Path(__file__).parent / "nb_src"
OUT = Path(__file__).resolve().parent.parent / "notebooks"

for src in sorted(SRC.glob("*.txt")):
    nb = nbformat.v4.new_notebook()
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    for chunk in ("\n" + src.read_text(encoding="utf-8")).split("\n%% ")[1:]:
        kind, _, body = chunk.partition("\n")
        make = nbformat.v4.new_markdown_cell if kind.strip() == "md" else nbformat.v4.new_code_cell
        nb.cells.append(make(body.strip("\n")))
    nbformat.write(nb, OUT / f"{src.stem}.ipynb")
    print("built", src.stem, len(nb.cells), "cells")
