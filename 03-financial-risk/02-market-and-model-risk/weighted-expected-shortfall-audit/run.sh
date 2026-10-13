#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 MPLBACKEND=Agg
python3 -c 'import sys; assert sys.version_info[:2] == (3,12), "Requires Python 3.12"'
python3 -m venv .venv
export PATH="$PWD/.venv/bin:$PATH"
python -m pip install --disable-pip-version-check -r requirements.lock.txt
mkdir -p results
python -m ruff check src tests benchmarks | tee results/lint.txt
python -m ruff format --check src tests benchmarks | tee results/format.txt
python -m mypy src benchmarks | tee results/types.txt
python -m pytest -q --cov=src.tail --cov=src.oracle --cov-branch --cov-report=term-missing --cov-report=json:results/coverage.json | tee results/tests.txt
python -m src.main | tee results/run.json
python benchmarks/build_notebook.py | tee results/notebook.txt
