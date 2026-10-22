#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ECON="$(cd "$HERE/../../.." && pwd)"
PROGRAM="$(cd "$HERE/.." && pwd)"
python3 -m venv "$HERE/.venv"
"$HERE/.venv/bin/python" -m pip install --disable-pip-version-check -q -r "$HERE/requirements.txt"
"$HERE/.venv/bin/ruff" check "$HERE/src" "$HERE/tests" "$HERE/benchmarks"
"$HERE/.venv/bin/mypy" --strict "$HERE/src"
"$HERE/.venv/bin/coverage" run --branch -m unittest discover -s "$HERE/tests" -v
"$HERE/.venv/bin/coverage" report -m | tee "$HERE/results/coverage.txt"
python3 -m unittest discover -s "$ECON/computational-economics/tests" -v 2>&1 | tee "$HERE/results/common-tests.txt"
"$HERE/.venv/bin/python" -m unittest discover -s "$PROGRAM/fire-sale-price-audit/tests" -v 2>&1 | tee "$HERE/results/fire-sale-regression.txt"
"$HERE/.venv/bin/python" -m unittest discover -s "$PROGRAM/coupled-clearing-audit/tests" -v 2>&1 | tee "$HERE/results/coupled-regression.txt"
"$HERE/.venv/bin/python" "$HERE/benchmarks/run.py"
(cd "$HERE" && "$HERE/.venv/bin/python" benchmarks/notebook.py)
"$HERE/.venv/bin/python" -m pip freeze | sort > "$HERE/environment-lock.txt"
printf 'Reproduced: %s\n' "$HERE"
