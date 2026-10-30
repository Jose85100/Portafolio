#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON=${PYTHON:-python3}
if [[ "${SKIP_INSTALL:-0}" != 1 ]]; then
  "$PYTHON" -m venv .venv
  PYTHON="$PWD/.venv/bin/python"
  "$PYTHON" -m pip install -r requirements.txt
fi
mkdir -p results/balancing30
"$PYTHON" -m unittest discover -s tests -v 2>&1 | tee results/balancing30/tests.txt
"$PYTHON" -m ruff check src tests benchmarks | tee results/balancing30/lint.txt
"$PYTHON" -m mypy src/splitter.py src/balancing.py --strict | tee results/balancing30/types.txt
"$PYTHON" -m src.balancing_experiment
"$PYTHON" benchmarks/execute_notebook.py notebook_balancing.ipynb
