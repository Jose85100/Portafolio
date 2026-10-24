#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m pip install -r requirements.txt --quiet
python -m ruff check src tests scripts_notebook.py
python -m mypy src --ignore-missing-imports
python -m coverage run --source=src.signatures -m unittest discover -s tests -v 2>&1 | tee results/tests.txt
python -m coverage report | tee results/coverage.txt
python -m coverage json -o results/coverage.json
python -m src.benchmark | tee results/run.txt
python scripts_notebook.py

# Preserve the expanded scientific notebook after the original builder.
REPO_ROOT=$(git rev-parse --show-toplevel)
DEPTH_PYTHON="${PYTHON:-python3}"
if [[ -x .venv/bin/python ]]; then DEPTH_PYTHON="$PWD/.venv/bin/python"; fi
"$DEPTH_PYTHON" "$REPO_ROOT/scripts/deepen_20261023_notebooks.py" --path "$PWD/notebook.ipynb"
"$DEPTH_PYTHON" "$REPO_ROOT/scripts/execute_research_depth.py" --one "$PWD/notebook.ipynb" --mode "${NOTEBOOK_EXECUTION_MODE:-ipython}"
