#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ -z "${PYTHON:-}" ]]; then
  if [[ ! -x .venv/bin/python ]]; then python3 -m venv --system-site-packages .venv; fi
  PYTHON="$PWD/.venv/bin/python"
fi
if [[ "${SKIP_INSTALL:-0}" != "1" ]]; then "$PYTHON" -m pip install -r requirements.txt; fi
mkdir -p results
"$PYTHON" -m coverage run --source=src.model,src.baseline -m unittest discover -s tests -v > results/tests.txt 2>&1
"$PYTHON" -m coverage json -o results/coverage.json
"$PYTHON" -m coverage report > results/coverage.txt
"$PYTHON" -m ruff check src tests benchmarks > results/lint.txt
"$PYTHON" -m mypy --config-file mypy.ini src/model.py src/baseline.py > results/types.txt
"$PYTHON" -m src.experiment > results/experiment.txt
"$PYTHON" benchmarks/build_notebook.py
