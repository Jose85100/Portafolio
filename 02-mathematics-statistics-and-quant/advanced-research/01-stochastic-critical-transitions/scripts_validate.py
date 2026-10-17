"""Verify delivery artifacts and record a machine-readable closure checklist."""

import csv
import json
from pathlib import Path

import nbformat
import numpy as np

ROOT = Path(__file__).resolve().parent


def main():
    required = ["README.md", "MVP.md", "informe.md", "referencias.bib", "config.json", "requirements.txt"]
    assert all((ROOT / name).is_file() for name in required)
    counts = {}
    for name, expected in (
        ("discretization.csv", 84),
        ("identification.csv", 3200),
        ("oracle.csv", 20),
        ("population.csv", 8),
        ("summary.csv", 16),
    ):
        with (ROOT / "benchmarks" / name).open() as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == expected, (name, len(rows))
        assert all(None not in row for row in rows), "extra CSV fields"
        counts[name] = len(rows)
    notebook = nbformat.read(ROOT / "notebook.ipynb", as_version=4)
    nbformat.validate(notebook)
    cells = [c for c in notebook.cells if c.cell_type == "code"]
    assert [c.execution_count for c in cells] == [1, 2, 3, 4]
    assert all(c.outputs for c in cells)
    assert not any(o.output_type == "error" for c in cells for o in c.outputs)
    image_outputs = [o for c in cells for o in c.outputs if "image/png" in o.get("data", {})]
    assert len(image_outputs) == 1
    assert (ROOT / "referencias.bib").read_text().count("@article{") == 6
    assert (ROOT / "benchmarks/audit.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    with np.load(ROOT / "benchmarks/example_paths.npz") as examples:
        assert len(examples.files) == 16
    result = json.loads((ROOT / "benchmarks/results.json").read_text())
    assert all(result["passed"].values())
    coverage = json.loads((ROOT / "benchmarks/coverage.json").read_text())["totals"]
    assert "43 passed" in (ROOT / "benchmarks/tests.txt").read_text()
    checklist = {
        "required_documents": required,
        "src_modules": sorted(p.name for p in (ROOT / "src").glob("*.py")),
        "csv_rows": counts,
        "notebook_executed_code_cells": len(cells),
        "notebook_png_outputs": len(image_outputs),
        "tests_passed": 43,
        "coverage_scope": "src/ou.py and src/reference.py only",
        "coverage_percent": coverage["percent_covered"],
        "all_gates_passed": True,
        "presentation_review": "Figure PNG visually inspected; notebook cells/outputs structurally checked. No full notebook-viewer visual QA in this environment.",
        "review_reproduction": "Open notebook.ipynb in Jupyter; optional: python -m pip install nbconvert && python -m jupyter nbconvert --to html notebook.ipynb",
    }
    (ROOT / "benchmarks/checklist.json").write_text(json.dumps(checklist, indent=2) + "\n")
    print(json.dumps(checklist, indent=2))


if __name__ == "__main__":
    main()
