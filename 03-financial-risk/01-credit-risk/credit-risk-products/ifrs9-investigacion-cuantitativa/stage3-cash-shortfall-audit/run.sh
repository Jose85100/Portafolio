#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -c 'import sys; assert sys.version_info[:2] == (3,12), "Requires Python3.12"'
python3 -m venv .venv
export PATH="$PWD/.venv/bin:$PATH"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 MPLBACKEND=Agg
python -m pip install --disable-pip-version-check -r requirements.lock.txt
mkdir -p results
ruff check src tests benchmarks | tee results/lint.txt
ruff format --check src tests benchmarks | tee results/format.txt
mypy src benchmarks | tee results/types.txt
python -m pytest -q --cov=src.model --cov=src.migration --cov-branch --cov-report=term-missing --cov-report=json:results/coverage.json | tee results/tests.txt
audit_python="$PWD/.venv/bin/python"
(cd .. && "$audit_python" -m unittest discover -s tests -v) 2>&1 | tee results/parent-tests.txt
python -m benchmarks.run | tee results/run.json
python -m benchmarks.migration | tee results/migration-run.json
python -m benchmarks.notebook | tee results/notebook.txt
