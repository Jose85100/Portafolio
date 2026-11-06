#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then python3 -m venv .venv; fi
.venv/bin/python -m pip install -q -r requirements.txt
.venv/bin/python -m unittest tests.test_uncertainty_structures -v
.venv/bin/ruff check src/uncertainty_structures.py tests/test_uncertainty_structures.py benchmarks/structured_uncertainty.py
.venv/bin/python -m mypy src/uncertainty_structures.py
.venv/bin/python benchmarks/structured_uncertainty.py
.venv/bin/python benchmarks/execute_structured_notebook.py
