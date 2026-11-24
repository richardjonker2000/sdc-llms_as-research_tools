"""Small helper so a coding agent can work with Jupyter notebooks without editing their JSON.

    .venv/bin/python .opencode/skills/notebook/nb.py show NOTEBOOK            list the cells: number, type, first line
    .venv/bin/python .opencode/skills/notebook/nb.py cell NOTEBOOK N          print cell N in full
    .venv/bin/python .opencode/skills/notebook/nb.py set  NOTEBOOK N FILE     replace cell N with the text of FILE
    .venv/bin/python .opencode/skills/notebook/nb.py add  NOTEBOOK N FILE [md] insert a new cell after cell N
    .venv/bin/python .opencode/skills/notebook/nb.py run  NOTEBOOK            run every cell, save the outputs in the notebook,
                                                                              print what each code cell printed
                                                                              and how many LLM answers were live, cache or fake

`run` stops at the first error and prints it with the cell number.
"""
import pathlib
import sys

import nbformat


def load(path):
    return nbformat.read(path, as_version=4)


def first_line(src):
    lines = [l for l in src.splitlines() if l.strip()]
    return (lines[0][:90] if lines else "(empty)") + (f"  [+{len(lines) - 1} lines]" if len(lines) > 1 else "")


def show(path):
    for i, c in enumerate(load(path).cells):
        print(f"{i:3d} {c.cell_type:4s} {first_line(c.source)}")


def cell(path, n):
    c = load(path).cells[int(n)]
    print(f"--- cell {n} ({c.cell_type}) ---\n{c.source}")


def set_cell(path, n, src_file):
    nb = load(path)
    nb.cells[int(n)].source = pathlib.Path(src_file).read_text(encoding="utf-8").rstrip("\n")
    if nb.cells[int(n)].cell_type == "code":
        nb.cells[int(n)].outputs, nb.cells[int(n)].execution_count = [], None
    nbformat.write(nb, path)
    print(f"cell {n} replaced. Now: {first_line(nb.cells[int(n)].source)}")


def add_cell(path, n, src_file, kind="code"):
    nb = load(path)
    text = pathlib.Path(src_file).read_text(encoding="utf-8").rstrip("\n")
    new = nbformat.v4.new_markdown_cell(text) if kind == "md" else nbformat.v4.new_code_cell(text)
    nb.cells.insert(int(n) + 1, new)
    nbformat.write(nb, path)
    print(f"new {kind} cell {int(n) + 1} added. The cells after it moved down by one: run `show` again.")


def text_of(output):
    if output.output_type == "stream":
        return output.text
    if output.output_type == "error":
        return f"ERROR {output.ename}: {output.evalue}"
    data = output.get("data", {})
    if "text/plain" in data:
        return data["text/plain"]
    return "[image]" if "image/png" in data else ""


def run(path):
    from nbclient import NotebookClient
    from nbclient.exceptions import CellExecutionError

    import collections, os, tempfile

    path = pathlib.Path(path)
    nb = load(path)
    log = pathlib.Path(tempfile.mkstemp(suffix=".log")[1])
    os.environ["WORKSHOP_CALL_LOG"] = str(log)        # the workshop helpers note every LLM answer here
    client = NotebookClient(nb, timeout=900, kernel_name="python3",
                            resources={"metadata": {"path": str(path.parent.resolve())}})
    failed = None
    try:
        client.execute()
    except CellExecutionError as e:
        failed = e
    nbformat.write(nb, path)
    for i, c in enumerate(nb.cells):
        if c.cell_type != "code" or not c.get("outputs"):
            continue
        out = "".join(text_of(o) for o in c.outputs).strip()
        if len(out) > 1500:
            out = out[:700] + "\n   [...]\n" + out[-700:]
        print(f"=== cell {i}: {first_line(c.source)}\n{out}\n")
    sources = collections.Counter(line.split("\t")[0] for line in log.read_text().splitlines() if line)
    log.unlink()
    if sources:
        print("LLM answers: " + ", ".join(f"{n} {k}" for k, n in sorted(sources.items()))
              + ("   <- FAKE answers (dry run): they test the code, they are NOT results" if sources.get("fake") else ""))
    if failed:
        print("RUN STOPPED AT AN ERROR (see the last cell above). Cells after it did not run.")
        sys.exit(1)
    print(f"Done: all cells ran. Outputs saved in {path}.")


if __name__ == "__main__":
    cmd, *args = sys.argv[1:] or ["help"]
    commands = {"show": show, "cell": cell, "set": set_cell, "add": add_cell, "run": run}
    if cmd not in commands:
        print(__doc__)
        sys.exit(1)
    commands[cmd](*args)
