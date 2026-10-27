#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
MATH_ENV="${MATH_ENV:-$PWD/.venv}"
python -m venv "$MATH_ENV"
"$MATH_ENV/bin/python" -m pip install -r requirements.txt --quiet
chmod u+x "$MATH_ENV/bin/ruff"
MATH_PY="$MATH_ENV/bin/python"
"$MATH_PY" -m ruff check src tests scripts_notebook.py
"$MATH_PY" -m mypy src --ignore-missing-imports
"$MATH_PY" -m coverage run --source=src.moments -m unittest discover -s tests -v 2>&1 | tee results/tests.txt
"$MATH_PY" -m coverage report | tee results/coverage.txt
"$MATH_PY" -m coverage json -o results/coverage.json
"$MATH_PY" -m src.benchmark | tee results/run.txt
"$MATH_PY" scripts_notebook.py
