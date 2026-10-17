#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m pip install -r requirements.txt
python -m pytest -q tests
python -m coverage run -m pytest -q tests
python -m coverage report -m --include="src/*"
python -m src
python -m src.report
python -m src.plot
