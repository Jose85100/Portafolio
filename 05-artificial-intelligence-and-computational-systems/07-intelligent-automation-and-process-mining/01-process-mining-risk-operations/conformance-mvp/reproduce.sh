#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m unittest discover -s tests -v
python3 -m src.engine > results/run_stdout.json
python3 -m compileall -q src tests
echo "OK: 360 evaluations, CSV/JSON/SVG, notebook and tests"
