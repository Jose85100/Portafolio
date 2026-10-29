#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
"$PYTHON" -m venv .venv
.venv/bin/python -m pip install --quiet -r requirements.txt
.venv/bin/python -m coverage run --source=src.monetary -m unittest discover -s tests -v
.venv/bin/python -m coverage report
.venv/bin/python -m ruff check src tests benchmarks
.venv/bin/python -m mypy src --ignore-missing-imports
.venv/bin/python -m src.run
.venv/bin/python benchmarks/notebook.py
