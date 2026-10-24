#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
if [[ "${REUSE_ENV:-0}" != 1 ]]; then
  "$PYTHON" -m venv .venv
  PYTHON="$PWD/.venv/bin/python"
  "$PYTHON" -m pip install -r requirements.txt
fi
"$PYTHON" -m coverage run --source=src -m unittest discover -s tests -v
"$PYTHON" -m coverage report | tee results/coverage.txt
"$PYTHON" -m ruff check --isolated src tests benchmarks
"$PYTHON" -m mypy src --strict
"$PYTHON" -m benchmarks.run
"$PYTHON" -m benchmarks.notebook

# Preserve the expanded scientific notebook after the original builder.
REPO_ROOT=$(git rev-parse --show-toplevel)
DEPTH_PYTHON="${PYTHON:-python3}"
if [[ -x .venv/bin/python ]]; then DEPTH_PYTHON="$PWD/.venv/bin/python"; fi
"$DEPTH_PYTHON" "$REPO_ROOT/scripts/deepen_20261023_notebooks.py" --path "$PWD/notebook.ipynb"
"$DEPTH_PYTHON" "$REPO_ROOT/scripts/execute_research_depth.py" --one "$PWD/notebook.ipynb" --mode "${NOTEBOOK_EXECUTION_MODE:-ipython}"

"$PYTHON" -m benchmarks.robust_run
"$PYTHON" -m benchmarks.robust_notebook
