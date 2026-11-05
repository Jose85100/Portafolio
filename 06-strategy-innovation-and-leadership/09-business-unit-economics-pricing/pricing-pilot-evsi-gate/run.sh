#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
python3 src/run.py
python3 benchmarks/benchmark.py > results/benchmark.jsonl
python3 scripts/generate_notebook.py
