"""Audit the complete MVP after reproduction."""

from __future__ import annotations

import json
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parent
required = [
    "README.md",
    "MVP.md",
    "informe.md",
    "referencias.bib",
    "fuentes.md",
    "requirements.txt",
    "Dockerfile",
    "config.json",
    "src/gauge.py",
    "src/benchmark.py",
    "tests/test_gauge.py",
    "benchmarks/raw.csv",
    "benchmarks/summary.csv",
    "benchmarks/results.json",
    "benchmarks/gauge-certificate.png",
    "benchmarks/tests.txt",
    "benchmarks/coverage.json",
    "notebook.ipynb",
]
missing = [path for path in required if not (ROOT / path).is_file()]
results = json.loads((ROOT / "benchmarks/results.json").read_text(encoding="utf-8"))
notebook = nbformat.read(ROOT / "notebook.ipynb", as_version=4)
code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
checks = {
    "no_missing_files": not missing,
    "all_predeclared_gates_pass": all(results["gates"].values()),
    "raw_rows_120": results["design"]["rows"] == 120,
    "notebook_has_outputs": bool(code_cells) and all(cell.execution_count for cell in code_cells),
    "notebook_no_errors": not any(
        output.output_type == "error" for cell in code_cells for output in cell.outputs
    ),
    "bibliography_at_least_five": (ROOT / "referencias.bib").read_text(encoding="utf-8").count("@") >= 5,
}
(ROOT / "benchmarks/checklist.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
if missing or not all(checks.values()):
    raise SystemExit(f"MVP audit failed: missing={missing}, checks={checks}")
print(json.dumps(checks, indent=2))
