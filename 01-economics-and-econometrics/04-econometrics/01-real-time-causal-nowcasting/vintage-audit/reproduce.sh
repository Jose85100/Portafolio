#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m ruff check src tests benchmarks
.venv/bin/python -m mypy src --ignore-missing-imports
.venv/bin/python -m coverage run --branch --source=src -m unittest discover -s tests -v 2>&1 | tee results/tests.log
.venv/bin/python -m coverage report -m | tee results/coverage.txt
.venv/bin/python -m unittest discover -s ../../../computational-economics/tests -v 2>&1 | tee results/common_tests.log
.venv/bin/python benchmarks/run.py > results/benchmark.log
.venv/bin/python benchmarks/costs.py
.venv/bin/python benchmarks/notebook.py
