#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
if [ "${SKIP_INSTALL:-0}" != "1" ]; then "$PYTHON" -m pip install -r requirements.txt; fi
"$PYTHON" -m unittest discover -s tests -v
"$PYTHON" -m src.experiment
"$PYTHON" benchmarks/execute_notebook.py
