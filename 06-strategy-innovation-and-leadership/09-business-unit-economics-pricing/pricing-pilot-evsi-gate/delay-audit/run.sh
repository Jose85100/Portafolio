#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p results
python3 -m unittest discover -s tests -v 2>&1 | tee results/tests.txt
python3 -m ruff check src/evsi_delay.py src/run_audit.py tests/test_evsi_delay.py scripts/execute_notebook.py scripts/validate_outputs.py
python3 -m py_compile src/evsi_delay.py src/run_audit.py tests/test_evsi_delay.py
python3 src/run_audit.py | tee results/run.txt
python3 scripts/execute_notebook.py | tee results/notebook_execution.txt
python3 scripts/validate_outputs.py | tee results/validation.txt
