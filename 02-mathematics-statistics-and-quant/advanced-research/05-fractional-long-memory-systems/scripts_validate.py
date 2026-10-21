"""Check delivery artifacts and make the exact verification scope explicit."""

import csv
import json
import re
from pathlib import Path

import nbformat
import numpy as np

ROOT = Path(__file__).resolve().parent


def main():
    required = ["README.md", "MVP.md", "informe.md", "referencias.bib", "config.json", "requirements.txt"]
    assert all((ROOT / p).is_file() for p in required)
    counts = {}
    for name, expected in (("raw.csv", 648), ("summary.csv", 216), ("setup.csv", 36), ("oracle.csv", 6)):
        with (ROOT / "benchmarks" / name).open() as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == expected, (name, len(rows))
        assert all(None not in row for row in rows)
        counts[name] = len(rows)
    nb = nbformat.read(ROOT / "notebook.ipynb", as_version=4)
    nbformat.validate(nb)
    cells = [c for c in nb.cells if c.cell_type == "code"]
    assert [c.execution_count for c in cells] == list(range(1, 9))
    assert all(c.outputs for c in cells)
    assert not any(o.output_type == "error" for c in cells for o in c.outputs)
    png = [o for c in cells for o in c.outputs if "image/png" in o.get("data", {})]
    assert len(png) == 1
    with np.load(ROOT / "benchmarks/inputs.npz") as inputs:
        assert len(inputs.files) == 12
    assert len(re.findall(r"@(?:article|misc)\{", (ROOT / "referencias.bib").read_text())) == 6
    results = json.loads((ROOT / "benchmarks/results.json").read_text())
    assert all(results["passed"].values())
    coverage = json.loads((ROOT / "benchmarks/coverage.json").read_text())["totals"]
    match = re.search(r"(\d+) passed", (ROOT / "benchmarks/tests.txt").read_text())
    assert match
    checklist = {
        "documents": required,
        "csv_rows": counts,
        "tests_passed": int(match.group(1)),
        "coverage_scope": "src/fractional.py and src/reference.py only",
        "coverage_percent": coverage["percent_covered"],
        "executed_code_cells": len(cells),
        "png_outputs": len(png),
        "all_gates_passed": True,
        "presentation_scope": "Figure visually inspected by author; notebook format/outputs checked and cells executed. Full notebook-viewer visual QA not claimed.",
        "finish_viewer_review": "Open notebook.ipynb in Jupyter; optionally install nbconvert and run python -m jupyter nbconvert --to html notebook.ipynb",
    }
    (ROOT / "benchmarks/checklist.json").write_text(json.dumps(checklist, indent=2) + "\n")
    print(json.dumps(checklist, indent=2))


if __name__ == "__main__":
    main()
