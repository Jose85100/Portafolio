"""Fail-closed artifact audit."""

import csv
import json
import re
from pathlib import Path
import nbformat
import numpy as np


def main():
    required = [
        "README.md",
        "MVP.md",
        "informe.md",
        "referencias.bib",
        "requirements.txt",
        "config.json",
        "Makefile",
    ]
    assert all(Path(p).is_file() for p in required)
    assert Path("referencias.bib").read_text().count("@") >= 5
    expected = {
        "replicates.csv": 1600,
        "summary.csv": 64,
        "timings.csv": 75,
        "oracle.csv": 12,
        "geodesics.csv": 132,
    }
    actual = {p: len(list(csv.DictReader((Path("benchmarks") / p).open()))) for p in expected}
    assert actual == expected
    assert np.load("benchmarks/counts.npz")["counts"].shape == (1600, 2, 32)
    result = json.loads(Path("benchmarks/results.json").read_text())
    assert all(result["passed"].values())
    nb = nbformat.read("notebook.ipynb", as_version=4)
    nbformat.validate(nb)
    cells = [c for c in nb.cells if c.cell_type == "code"]
    assert [c.execution_count for c in cells] == list(range(1, 7))
    assert all(c.outputs for c in cells)
    assert not any(o.output_type == "error" for c in cells for o in c.outputs)
    pngs = sum("image/png" in o.get("data", {}) for c in cells for o in c.outputs)
    assert pngs == 1 and Path("benchmarks/audit.png").stat().st_size > 10000
    log = Path("benchmarks/tests.txt").read_text()
    tests = int(re.search(r"(\d+) passed", log)[1])
    coverage = json.loads(Path("benchmarks/coverage.json").read_text())["totals"]["percent_covered"]
    check = {
        "required_documents": required,
        "csv_rows": actual,
        "tests_passed": tests,
        "coverage_numeric_modules_percent": coverage,
        "coverage_scope": "geometry.py, testing.py, reference.py only",
        "executed_code_cells": 6,
        "png_outputs": pngs,
        "all_gates_passed": True,
        "visual_scope": "Figure inspected separately; full notebook-viewer visual QA not claimed. Open notebook in Jupyter or export HTML using nbconvert.",
    }
    Path("benchmarks/checklist.json").write_text(json.dumps(check, indent=2) + "\n")
    print(json.dumps(check, indent=2))


if __name__ == "__main__":
    main()
