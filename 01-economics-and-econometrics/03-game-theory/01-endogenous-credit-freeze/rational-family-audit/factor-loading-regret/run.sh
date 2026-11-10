#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then python3 -m venv .venv; fi
.venv/bin/python -m pip install -q -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v 2>&1 | tee results/tests.log
.venv/bin/python -m ruff check src tests benchmarks.py 2>&1 | tee results/lint.log
.venv/bin/mypy src/robust_regret.py 2>&1 | tee results/types.log
.venv/bin/python benchmarks.py 2>&1 | tee results/run.log
.venv/bin/python execute_notebook.py 2>&1 | tee results/notebook.log
.venv/bin/python -m pip freeze > environment-lock.txt
