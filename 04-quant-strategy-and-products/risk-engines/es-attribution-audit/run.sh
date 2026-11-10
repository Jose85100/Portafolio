#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
mkdir -p results
python -m unittest discover -s tests -v 2>&1 | tee results/tests.txt
python -m compileall -q src tests run.py
if command -v ruff >/dev/null 2>&1; then ruff check src tests run.py 2>&1 | tee results/lint.txt; else echo 'ruff: no instalado; omitido' | tee results/lint.txt; fi
if command -v mypy >/dev/null 2>&1; then mypy --strict src/es_attribution.py 2>&1 | tee results/types.txt; else echo 'mypy: no instalado; omitido' | tee results/types.txt; fi
python run.py
