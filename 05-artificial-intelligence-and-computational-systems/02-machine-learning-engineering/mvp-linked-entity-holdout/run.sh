#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON=${PYTHON:-python3}
if [[ "${SKIP_INSTALL:-0}" != 1 ]]; then
  "$PYTHON" -m venv .venv
  PYTHON="$PWD/.venv/bin/python"
  "$PYTHON" -m pip install -r requirements.txt
fi
mkdir -p results
"$PYTHON" -m unittest discover -s tests -v 2>&1 | tee results/tests.txt
"$PYTHON" -m ruff check src tests benchmarks | tee results/lint.txt
"$PYTHON" -m mypy src/splitter.py --strict | tee results/types.txt
"$PYTHON" -m src.experiment
"$PYTHON" benchmarks/execute_notebook.py
