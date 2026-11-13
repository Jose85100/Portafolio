#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
python3 src/run.py
python3 benchmarks/benchmark.py > results/benchmark.jsonl
python3 scripts/generate_notebook.py
PYTHONPATH=src python3 src/run_prior_sensitivity.py > results/prior_sensitivity_run.txt
python3 scripts/execute_prior_notebook.py > results/prior_sensitivity_notebook.txt
