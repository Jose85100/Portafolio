#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON=${PYTHON:-python3}
if [[ "${SKIP_INSTALL:-0}" != 1 ]]; then
  "$PYTHON" -m venv .venv
  PYTHON="$PWD/.venv/bin/python"
  "$PYTHON" -m pip install -r requirements.txt
fi
if [[ -f "$(dirname "$PYTHON")/ruff" ]]; then chmod +x "$(dirname "$PYTHON")/ruff"; fi
mkdir -p results/temporal1103
"$PYTHON" -m unittest discover -s tests -v 2>&1 | tee results/temporal1103/tests.txt
"$PYTHON" -m ruff check src tests benchmarks 2>&1 | tee results/temporal1103/lint.txt
"$PYTHON" -m mypy src/temporal_revisions.py src/revision_experiment.py --strict 2>&1 | tee results/temporal1103/types.txt
"$PYTHON" -m pip freeze > results/temporal1103/versions.txt
"$PYTHON" -m src.revision_experiment
"$PYTHON" benchmarks/execute_notebook.py notebook_temporal1103.ipynb
