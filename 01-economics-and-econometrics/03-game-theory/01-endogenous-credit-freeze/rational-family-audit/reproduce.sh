#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p results
python3 -m venv .venv
# Source wheels need a complete GNU toolchain; override missing LLVM paths in some Python builds.
CC=gcc CXX=g++ AR=ar RANLIB=ranlib LDSHARED='g++ -shared' .venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m ruff check src tests benchmarks 2>&1 | tee results/lint.log
.venv/bin/python -m mypy src --ignore-missing-imports 2>&1 | tee results/types.log
.venv/bin/python -m coverage run --branch --source=src -m unittest discover -s tests -v 2>&1 | tee results/tests.log
.venv/bin/python -m coverage report -m | tee results/coverage.txt
.venv/bin/python -m unittest discover -s ../strategic-form-audit/tests -v 2>&1 | tee results/strategic_tests.log
.venv/bin/python -m unittest discover -s ../polyhedral-freeze-audit/tests -v 2>&1 | tee results/polyhedral_tests.log
.venv/bin/python -m unittest discover -s ../mixed-equilibrium-audit/tests -v 2>&1 | tee results/mixed_tests.log
.venv/bin/python -m unittest discover -s ../bayesian-freeze-audit/tests -v 2>&1 | tee results/pure_tests.log
.venv/bin/python -m unittest discover -s ../../../computational-economics/tests -v 2>&1 | tee results/common_tests.log
.venv/bin/python benchmarks/run.py | tee results/benchmark.log
.venv/bin/python benchmarks/notebook.py
.venv/bin/python -m pip freeze > environment-lock.txt
