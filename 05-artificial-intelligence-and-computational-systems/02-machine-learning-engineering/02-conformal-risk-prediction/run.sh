#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
if [ "${SKIP_INSTALL:-0}" != "1" ]; then "$PYTHON" -m pip install -r requirements.txt; fi
"$PYTHON" -m unittest discover -s tests -v
"$PYTHON" -m src.experiment
"$PYTHON" benchmarks/execute_notebook.py

# Preserve the expanded scientific notebook after the original builder.
REPO_ROOT=$(git rev-parse --show-toplevel)
DEPTH_PYTHON="${PYTHON:-python3}"
if [[ -x .venv/bin/python ]]; then DEPTH_PYTHON="$PWD/.venv/bin/python"; fi
"$DEPTH_PYTHON" "$REPO_ROOT/scripts/deepen_20261023_notebooks.py" --path "$PWD/notebook.ipynb"
"$DEPTH_PYTHON" "$REPO_ROOT/scripts/execute_research_depth.py" --one "$PWD/notebook.ipynb" --mode "${NOTEBOOK_EXECUTION_MODE:-ipython}"
