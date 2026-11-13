#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p results
python3 -m venv .venv
if [ -f environment-lock.txt ]; then
  .venv/bin/python -m pip install -r environment-lock.txt
else
  .venv/bin/python -m pip install -r requirements.txt
fi
.venv/bin/python -m ruff check src tests benchmarks 2>&1 | tee results/lint.log
.venv/bin/python -m mypy src --strict 2>&1 | tee results/types.log
.venv/bin/python -m coverage run --branch --source=src -m unittest discover -s tests -v 2>&1 | tee results/tests.log
.venv/bin/python -m coverage report -m | tee results/coverage.txt
.venv/bin/python -m unittest discover -s ../../../computational-economics/tests -v 2>&1 | tee results/common_tests.log
.venv/bin/python -m unittest discover -s ../sovereign-clearing-audit/tests -v 2>&1 | tee results/clearing_tests.log
.venv/bin/python -m unittest discover -s ../fire-sale-price-audit/tests -v 2>&1 | tee results/market_tests.log
.venv/bin/python benchmarks/run.py | tee results/benchmark.log
.venv/bin/python benchmarks/notebook.py
.venv/bin/python -m unittest discover -s ../../../research-agents/tests -v 2>&1 | tee results/review_tests.log
.venv/bin/python ../../../research-agents/review.py --output results/static_review.json 2>&1 | tee results/static_review.log
.venv/bin/python -m pip freeze > environment-lock.txt
