#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON=${PYTHON:-python3}
if [[ "${SKIP_INSTALL:-0}" != "1" ]]; then
  "$PYTHON" -m pip install -r requirements.txt
fi
mkdir -p results
"$PYTHON" -m coverage run --source=src.conformal -m unittest discover -s tests -v > results/tests.txt 2>&1
"$PYTHON" -m coverage json -o results/coverage.json
"$PYTHON" -m coverage report > results/coverage.txt
"$PYTHON" -m ruff check src tests benchmarks > results/lint.txt
"$PYTHON" -m mypy src/conformal.py > results/types.txt
"$PYTHON" -m src.experiment > results/experiment.txt
"$PYTHON" benchmarks/build_notebook.py
