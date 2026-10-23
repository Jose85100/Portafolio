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
"$PYTHON" -m ruff check src tests benchmarks
"$PYTHON" -m mypy src --strict
"$PYTHON" -m benchmarks.run
"$PYTHON" -m benchmarks.notebook
