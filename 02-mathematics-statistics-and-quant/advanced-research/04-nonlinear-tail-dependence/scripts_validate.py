"""Machine-readable closure checks; do not substitute these for visual inspection."""

import csv
import json
import re
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parent


def main():
    required = ["README.md", "MVP.md", "informe.md", "referencias.bib", "config.json", "requirements.txt"]
    assert all((ROOT / name).is_file() for name in required)
    counts = {}
    for name, expected in (
        ("population.csv", 48),
        ("raw.csv", 1280),
        ("summary.csv", 16),
        ("memory.csv", 16),
        ("rank_check.csv", 3),
    ):
        with (ROOT / "benchmarks" / name).open() as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == expected, (name, len(rows))
        assert all(None not in row for row in rows)
        counts[name] = len(rows)
    notebook = nbformat.read(ROOT / "notebook.ipynb", as_version=4)
    nbformat.validate(notebook)
    cells = [c for c in notebook.cells if c.cell_type == "code"]
    assert [c.execution_count for c in cells] == list(range(1, 9))
    assert all(c.outputs for c in cells)
    assert not any(o.output_type == "error" for c in cells for o in c.outputs)
    png = [o for c in cells for o in c.outputs if "image/png" in o.get("data", {})]
    assert len(png) == 1
    assert len(re.findall(r"@(?:article|book|incollection)\{", (ROOT / "referencias.bib").read_text())) == 5
    r = json.loads((ROOT / "benchmarks/results.json").read_text())
    assert all(r["passed"].values())
    coverage = json.loads((ROOT / "benchmarks/coverage.json").read_text())["totals"]
    match = re.search(r"(\d+) passed", (ROOT / "benchmarks/tests.txt").read_text())
    assert match
    checklist = {
        "required_documents": required,
        "csv_rows": counts,
        "tests_passed": int(match.group(1)),
        "coverage_scope": "src/copulas.py and src/reference.py only",
        "coverage_percent": coverage["percent_covered"],
        "executed_code_cells": len(cells),
        "png_outputs": len(png),
        "all_gates_passed": True,
        "presentation_scope": "Figure inspected by author; notebook structurally validated and actually executed. Full notebook-viewer visual QA not claimed.",
        "complete_visual_review": "Open notebook.ipynb in Jupyter, or install nbconvert and run python -m jupyter nbconvert --to html notebook.ipynb",
    }
    (ROOT / "benchmarks/checklist.json").write_text(json.dumps(checklist, indent=2) + "\n")
    print(json.dumps(checklist, indent=2))


if __name__ == "__main__":
    main()
