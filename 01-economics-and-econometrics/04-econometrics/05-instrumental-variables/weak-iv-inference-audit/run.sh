#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
"$PYTHON" -m venv .venv
.venv/bin/python -m pip install --quiet -r requirements.txt
.venv/bin/python -m coverage run --source=src.inference -m unittest discover -s tests -v
.venv/bin/python -m coverage report
.venv/bin/python -m ruff check src tests benchmarks
.venv/bin/python -m mypy src --ignore-missing-imports
.venv/bin/python -m src.run
.venv/bin/python -m benchmarks.costs
.venv/bin/python benchmarks/execute_notebook.py

# Preserve the expanded scientific notebook after the original builder.
REPO_ROOT=$(git rev-parse --show-toplevel)
DEPTH_PYTHON="${PYTHON:-python3}"
if [[ -x .venv/bin/python ]]; then DEPTH_PYTHON="$PWD/.venv/bin/python"; fi
"$DEPTH_PYTHON" "$REPO_ROOT/scripts/deepen_20261023_notebooks.py" --path "$PWD/notebook.ipynb"
"$DEPTH_PYTHON" "$REPO_ROOT/scripts/execute_research_depth.py" --one "$PWD/notebook.ipynb" --mode "${NOTEBOOK_EXECUTION_MODE:-ipython}"
