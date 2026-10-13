#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m ruff check src tests main.py benchmarks
.venv/bin/python -m pytest tests -q --cov=src --cov-branch --cov-report=json:results/coverage.json --cov-report=term
.venv/bin/python main.py
.venv/bin/python benchmarks/execute_notebook.py
