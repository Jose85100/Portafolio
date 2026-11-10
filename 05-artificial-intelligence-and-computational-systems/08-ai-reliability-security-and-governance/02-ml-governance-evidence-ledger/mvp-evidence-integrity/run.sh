#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
python run_experiment.py
python -m unittest discover -s tests -v
ruff check src tests run_experiment.py execute_notebook.py
mypy src tests
python execute_notebook.py
