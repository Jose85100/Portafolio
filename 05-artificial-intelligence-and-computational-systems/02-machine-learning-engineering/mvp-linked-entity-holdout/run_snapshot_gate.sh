#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON=${PYTHON:-python3}
if [[ "${SKIP_INSTALL:-0}" != 1 ]]; then
  "$PYTHON" -m venv .venv
  PYTHON="$PWD/.venv/bin/python"
  "$PYTHON" -m pip install -r requirements.txt
fi
mkdir -p results/snapshot1102
"$PYTHON" -m unittest discover -s tests -v 2>&1 | tee results/snapshot1102/tests.txt
"$PYTHON" -m ruff check src tests benchmarks | tee results/snapshot1102/lint.txt
"$PYTHON" -m mypy src/splitter.py src/balancing.py src/graph_audit.py src/partial_audit.py src/snapshot_gate.py --strict | tee results/snapshot1102/types.txt
"$PYTHON" -m pip freeze > results/snapshot1102/versions.txt
"$PYTHON" -m src.snapshot_experiment
"$PYTHON" benchmarks/execute_notebook.py notebook_snapshot_gate.ipynb
