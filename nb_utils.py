"""Shared helpers for building this course's Jupyter notebooks programmatically.

Every module notebook is built by a small Python script that imports this
module, assembles a list of cells, and writes the .ipynb file. Keeping all
notebooks generated from code (instead of hand-edited JSON) makes the house
style consistent across all 6 modules.

Cell pattern for every exercise (do not deviate — forks/other builders must
match this exactly so the course feels like one product):

    md(problem_statement)                  # "### Exercise N.M: <title>" + prompt
    code(stub_code)                        # student fills in, has `raise NotImplementedError`
    code(check_code)                       # try/except assert block, prints PASS/FAIL
    md(hint_block(hint_text))              # collapsed <details> hint
    md(solution_block(solution_code))      # collapsed <details> solution (shown as text, not run)

`<details>` is used instead of a Jupyter extension because it renders
correctly with zero setup in classic Jupyter, JupyterLab, nbviewer AND
Google Colab — no nbextensions required.
"""
import nbformat as nbf


def md(text: str) -> dict:
    return nbf.v4.new_markdown_cell(text.strip() + "\n")


def code(source: str) -> dict:
    return nbf.v4.new_code_cell(source.strip() + "\n")


def hint_block(hint_text: str) -> str:
    return (
        "<details>\n"
        "<summary>💡 Hint (click to expand)</summary>\n\n"
        f"{hint_text.strip()}\n\n"
        "</details>"
    )


def solution_block(solution_code: str) -> str:
    return (
        "<details>\n"
        "<summary>✅ Solution (click to expand)</summary>\n\n"
        "```python\n"
        f"{solution_code.strip()}\n"
        "```\n\n"
        "</details>"
    )


def exercise_cells(
    number: str,
    title: str,
    problem: str,
    stub: str,
    check: str,
    hint: str,
    solution: str,
) -> list:
    """Build the standard 5-cell exercise block described in the module docstring."""
    problem_md = f"### 💪 Exercise {number}: {title}\n\n{problem.strip()}"
    return [
        md(problem_md),
        code(stub),
        code(check),
        md(hint_block(hint)),
        md(solution_block(solution)),
    ]


def colab_badge(notebook_filename: str, repo: str = "inigoochoa/comprehensive-numpy") -> str:
    """Markdown Colab badge. `repo` is a placeholder until the course is pushed to GitHub —
    see the project README for the find/replace instructions."""
    url = f"https://colab.research.google.com/github/{repo}/blob/main/{notebook_filename}"
    return f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({url})"


def build_notebook(title: str, filename: str, intro_cells: list, lesson_cells: list) -> dict:
    """Assemble final notebook: title + colab badge + intro cells, then all lesson cells."""
    header = [
        md(f"# {title}"),
        md(colab_badge(filename)),
    ]
    cells = header + intro_cells + lesson_cells
    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.x"},
    }
    return nb


def save_notebook(nb: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    nbf.validate(nb)
