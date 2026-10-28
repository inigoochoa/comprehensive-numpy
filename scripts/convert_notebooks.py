"""Convert the 6 course notebooks into the Astro website's content collection.

Source of truth: module_1_fundamentals.ipynb ... module_6_performance_projects.ipynb
(repo root). Output: web/src/content/lessons/module-N/*.mdx + web/src/data/exercises.json

Run with: python scripts/convert_notebooks.py
Re-run any time a build_module_N.py script changes and you regenerate its .ipynb —
this script never edits the notebooks, only reads them.
"""
import copy
import json
import re
import sys
from pathlib import Path

import nbformat as nbf
import yaml
from nbclient import NotebookClient

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
CONTENT_DIR = WEB / "src" / "content" / "lessons"
DATA_DIR = WEB / "src" / "data"
COLAB_REPO_PLACEHOLDER = "inigoochoa/comprehensive-numpy"

MODULES = [
    (1, "Fundamentals & Array Creation", "module_1_fundamentals.ipynb"),
    (2, "Indexing, Slicing & Views", "module_2_indexing_views.ipynb"),
    (3, "Array Operations & Broadcasting", "module_3_operations_broadcasting.ipynb"),
    (4, "Aggregations, Statistics & Sorting", "module_4_aggregations_statistics.ipynb"),
    (5, "Linear Algebra & Random", "module_5_linalg_random.ipynb"),
    (6, "Performance, I/O & Mini-Projects", "module_6_performance_projects.ipynb"),
]

LESSON_RE = re.compile(r"^##\s+Lesson\s+(\d+)\s+—\s+(.+)$", re.M)
EXERCISE_RE = re.compile(r"^###\s+💪\s+Exercise\s+(\S+):\s*(.+)$", re.M)
HINT_RE = re.compile(r"<summary>💡 Hint.*?</summary>\s*(.*?)\s*</details>", re.S)
SOLUTION_RE = re.compile(r"<summary>✅ Solution.*?</summary>\s*```python\s*(.*?)```", re.S)
SECTION_BREAK_RE = re.compile(r"^##\s+(🎯 Key Takeaways|🎓 Course Complete!)", re.M)


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[`*]", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:60] or "section"


def patch_stub_cells(cells):
    """Deep-copy cells, replacing every exercise stub with its own solution so the
    whole module executes cleanly and every example cell gets a real output."""
    cells = copy.deepcopy(cells)
    solutions = [
        SOLUTION_RE.search(c["source"]).group(1).strip()
        for c in cells
        if c["cell_type"] == "markdown" and SOLUTION_RE.search(c["source"])
    ]
    sol_iter = iter(solutions)
    for c in cells:
        if c["cell_type"] == "code" and "raise NotImplementedError" in c["source"]:
            c["source"] = next(sol_iter)
    return cells


def execute_for_outputs(cells):
    """Return outputs[i] == list of nbformat output dicts for original cells[i],
    by executing a patched+matplotlib-inline-enabled copy and stripping the
    magic cell we prepended back off again."""
    magic_cell = nbf.v4.new_code_cell("%matplotlib inline")
    patched = [magic_cell] + patch_stub_cells(cells)
    nb = nbf.v4.new_notebook()
    nb["cells"] = patched
    nb["metadata"] = {"kernelspec": {"name": "python3", "language": "python", "display_name": "Python 3"}}
    client = NotebookClient(nb, timeout=120, kernel_name="python3")
    client.execute()
    return [c.get("outputs", []) for c in nb["cells"][1:]]


def render_outputs_md(outputs) -> str:
    raw_parts = []
    for out in outputs:
        if out.get("output_type") == "stream":
            text = out.get("text", "").strip()
            if text:
                raw_parts.append(("text", text))
        elif out.get("output_type") in ("execute_result", "display_data"):
            data = out.get("data", {})
            if "image/png" in data:
                raw_parts.append(("image", data["image/png"]))
            elif "text/plain" in data:
                text = "".join(data["text/plain"]).strip()
                if text:
                    raw_parts.append(("text", text))
    # Merge consecutive text chunks (e.g. two separate print()s) into one block.
    parts = []
    for kind, value in raw_parts:
        if kind == "text" and parts and parts[-1][0] == "text":
            parts[-1] = ("text", parts[-1][1] + "\n" + value)
        else:
            parts.append((kind, value))
    if not parts:
        return ""
    chunks = ["\n**Output:**\n"]
    for kind, value in parts:
        if kind == "image":
            chunks.append(f'\n<img class="cell-output-image" alt="plot output" src="data:image/png;base64,{value}" />\n')
        else:
            escaped = value.replace("```", "ʼʼʼ")
            chunks.append(f"\n```text\n{escaped}\n```\n")
    return "".join(chunks)


def split_into_lessons(cells):
    """Return (intro_cells, [ (lesson_number, title, cells) , ... ]) splitting on
    `## Lesson N — Title` markdown headers. Trailing Key Takeaways / Course
    Complete cells attach to the last lesson group."""
    first_lesson_idx = None
    for i, c in enumerate(cells):
        if c["cell_type"] == "markdown" and LESSON_RE.match(c["source"]):
            first_lesson_idx = i
            break
    if first_lesson_idx is None:
        raise ValueError("No '## Lesson N — Title' header found")

    intro_cells = cells[:first_lesson_idx]
    groups = []
    current = None
    for c in cells[first_lesson_idx:]:
        if c["cell_type"] == "markdown":
            m = LESSON_RE.match(c["source"])
            if m:
                current = {"number": int(m.group(1)), "title": m.group(2).strip(), "cells": []}
                groups.append(current)
                remainder = c["source"][m.end():].lstrip("\n")
                if remainder.strip():
                    current["cells"].append({"cell_type": "markdown", "source": remainder})
                continue
        current["cells"].append(c)
    return intro_cells, groups


def build_lesson_body(cells, outputs_for_cells, exercises, module_num):
    """Walk a lesson's cell list (outputs_for_cells is a dict id(cell)->outputs for
    non-exercise code cells), emitting MDX body text and collecting exercises."""
    body = []
    i = 0
    while i < len(cells):
        cell = cells[i]
        if cell["cell_type"] == "markdown":
            m = EXERCISE_RE.match(cell["source"])
            if m:
                local_id, ex_title = m.group(1), m.group(2).strip()
                ex_id = f"m{module_num}-{local_id}"
                problem = cell["source"].split("\n", 1)[1].strip() if "\n" in cell["source"] else ""
                stub_cell, check_cell, hint_cell, solution_cell = cells[i + 1 : i + 5]
                hint_match = HINT_RE.search(hint_cell["source"])
                solution_match = SOLUTION_RE.search(solution_cell["source"])
                exercises[ex_id] = {
                    "localId": local_id,
                    "title": ex_title,
                    "problem": problem,
                    "stub": stub_cell["source"].strip() + "\n",
                    "check": check_cell["source"].strip() + "\n",
                    "hint": hint_match.group(1).strip() if hint_match else "",
                    "solution": solution_match.group(1).strip() + "\n" if solution_match else "",
                }
                body.append(f'\n<Exercise id="{ex_id}" client:visible />\n')
                i += 5
                continue
            if SECTION_BREAK_RE.match(cell["source"]):
                body.append("\n---\n\n" + cell["source"].strip() + "\n")
                i += 1
                continue
            body.append("\n" + cell["source"].strip() + "\n")
            i += 1
        else:  # example code cell
            body.append(f"\n```python\n{cell['source'].strip()}\n```\n")
            body.append(render_outputs_md(outputs_for_cells.get(id(cell), [])))
            i += 1
    return "".join(body)


def frontmatter(data) -> str:
    return "---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True) + "---\n\n"


def main():
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    all_exercises = {}
    sidebar_toc = []

    for module_num, module_title, filename in MODULES:
        nb = nbf.read(ROOT / filename, as_version=4)
        cells = nb["cells"]
        outputs = execute_for_outputs(cells)
        outputs_by_id = {id(c): out for c, out in zip(cells, outputs)}

        intro_cells, lesson_groups = split_into_lessons(cells)
        module_dir = CONTENT_DIR / f"module-{module_num}"
        module_dir.mkdir(parents=True, exist_ok=True)

        # --- module overview page (welcome + goals, skip the "import numpy" setup cell) ---
        overview_md = "\n".join(
            c["source"].strip() for c in intro_cells if c["cell_type"] == "markdown"
        )
        overview_fm = frontmatter(
            {
                "title": f"Module {module_num} Overview",
                "module": module_num,
                "moduleTitle": module_title,
                "lessonNumber": None,
                "order": module_num * 100,
                "notebookFile": filename,
                "colabRepo": COLAB_REPO_PLACEHOLDER,
                "exerciseIds": [],
                "kind": "overview",
            }
        )
        (module_dir / "00-overview.mdx").write_text(
            overview_fm + overview_md + "\n", encoding="utf-8"
        )

        lessons_toc = []
        for group in lesson_groups:
            lesson_exercises = {}
            body = build_lesson_body(group["cells"], outputs_by_id, lesson_exercises, module_num)
            all_exercises.update(lesson_exercises)

            clean_title = group["title"].replace("`", "")
            fm = frontmatter(
                {
                    "title": clean_title,
                    "module": module_num,
                    "moduleTitle": module_title,
                    "lessonNumber": group["number"],
                    "order": module_num * 100 + group["number"],
                    "notebookFile": filename,
                    "colabRepo": COLAB_REPO_PLACEHOLDER,
                    "exerciseIds": list(lesson_exercises.keys()),
                    "kind": "lesson",
                }
            )
            slug = f"{group['number']:02d}-{slugify(clean_title)}"
            import_line = (
                'import Exercise from "../../../components/Exercise";\n\n'
                if lesson_exercises
                else ""
            )
            (module_dir / f"{slug}.mdx").write_text(
                fm + import_line + body + "\n", encoding="utf-8"
            )
            lessons_toc.append(
                {
                    "number": group["number"],
                    "title": clean_title,
                    "slug": slug,
                    "exerciseIds": list(lesson_exercises.keys()),
                }
            )

        sidebar_toc.append(
            {"module": module_num, "title": module_title, "lessons": lessons_toc}
        )
        print(f"[{filename}] -> {len(lesson_groups)} lessons, "
              f"{sum(len(g['cells']) for g in lesson_groups)} cells processed")

    (DATA_DIR / "exercises.json").write_text(
        json.dumps(all_exercises, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (DATA_DIR / "toc.json").write_text(
        json.dumps(sidebar_toc, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Wrote {len(all_exercises)} exercises to {DATA_DIR / 'exercises.json'}")
    print(f"Wrote table of contents to {DATA_DIR / 'toc.json'}")


if __name__ == "__main__":
    main()
