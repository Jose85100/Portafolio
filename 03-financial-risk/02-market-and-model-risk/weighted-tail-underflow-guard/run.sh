#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -c 'import sys; assert sys.version_info[:2] == (3,12), "Requires Python 3.12"'
python3 -m venv .venv
export PATH="$PWD/.venv/bin:$PATH"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python -m pip install --disable-pip-version-check -r requirements.lock.txt
mkdir -p results
ruff check src tests benchmarks | tee results/lint.txt
ruff format --check src tests benchmarks | tee results/format.txt
mypy src benchmarks | tee results/types.txt
python -m pytest -q --cov=src.guard --cov=src.consumer --cov=src.packet --cov-branch --cov-report=term-missing --cov-report=json:results/coverage.json | tee results/tests.txt
python -m benchmarks.run | tee results/run.json
python -m benchmarks.consumer | tee results/consumer-run.json
python -m benchmarks.packet | tee results/packet-run.json
python benchmarks/notebook.py | tee results/notebook.txt
