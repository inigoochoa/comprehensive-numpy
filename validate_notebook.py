"""Validate a module notebook: structural check + full execution with every
exercise stub swapped for its own "Solution" block, so we catch broken
examples AND broken reference solutions before shipping.

Usage: python validate_notebook.py module_1_fundamentals.ipynb
"""
import copy
import re
import sys

import nbformat as nbf
from nbclient import NotebookClient

sys.stdout.reconfigure(encoding="utf-8")

SOLUTION_RE = re.compile(
    r"<summary>✅ Solution.*?</summary>\s*```python\s*(.*?)```", re.S
)


def extract_solutions(cells):
    """Return list of solution code blocks found in markdown cells, in order."""
    solutions = []
    for cell in cells:
        if cell["cell_type"] == "markdown":
            m = SOLUTION_RE.search(cell["source"])
            if m:
                solutions.append(m.group(1).strip())
    return solutions


def patch_stubs_with_solutions(nb):
    """Return a deep copy of nb where every code cell containing
    `raise NotImplementedError` has its source replaced by the next
    available extracted solution, in document order. The check cell right
    after each patched stub (our 5-cell exercise layout: problem, stub,
    check, hint, solution) gets an extra `assert _passed` appended in this
    patched copy only, so a check that silently leaves `_passed` False even
    with the correct solution fails validation instead of shipping quietly."""
    nb = copy.deepcopy(nb)
    solutions = extract_solutions(nb["cells"])
    sol_iter = iter(solutions)
    cells = nb["cells"]
    patched, skipped = 0, 0
    for i, cell in enumerate(cells):
        if cell["cell_type"] == "code" and "raise NotImplementedError" in cell["source"]:
            try:
                cell["source"] = next(sol_iter)
                patched += 1
            except StopIteration:
                skipped += 1
                continue
            check_cell = cells[i + 1]
            assert check_cell["cell_type"] == "code", "expected check cell after stub"
            check_cell["source"] = (
                check_cell["source"].rstrip()
                + '\n\nassert _passed, "reference solution did not set _passed=True"\n'
            )
    return nb, patched, skipped


def main(path):
    nb = nbf.read(path, as_version=4)
    nbf.validate(nb)
    print(f"[{path}] schema OK, {len(nb['cells'])} cells")

    patched_nb, patched, skipped = patch_stubs_with_solutions(nb)
    print(f"[{path}] patched {patched} stub(s) with extracted solutions"
          + (f", {skipped} stub(s) had NO solution found!" if skipped else ""))

    client = NotebookClient(patched_nb, timeout=120, kernel_name="python3")
    try:
        client.execute()
        print(f"[{path}] ✅ EXECUTION OK (all cells, solutions included, ran clean)")
    except Exception as e:
        print(f"[{path}] ❌ EXECUTION FAILED: {e}")
        raise


if __name__ == "__main__":
    for p in sys.argv[1:]:
        main(p)
