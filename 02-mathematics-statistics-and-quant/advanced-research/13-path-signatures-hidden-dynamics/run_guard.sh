#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
# Dedicated environment prevents concurrent research jobs changing tool versions.
GUARD_ENV="${GUARD_ENV:-$PWD/.venv-guard}"
python -m venv "$GUARD_ENV"
"$GUARD_ENV/bin/python" -m pip install -r requirements.txt --quiet
# Some execution hosts restore wheel entry points without executable mode.
chmod u+x "$GUARD_ENV/bin/ruff"
GUARD_PY="$GUARD_ENV/bin/python"
"$GUARD_PY" -m ruff check src/aliasing_guard.py src/benchmark_guard.py tests/test_aliasing_guard.py scripts_notebook_guard.py
"$GUARD_PY" -m mypy src/aliasing_guard.py src/benchmark_guard.py --ignore-missing-imports
"$GUARD_PY" -m coverage run --source=src.aliasing_guard -m unittest discover -s tests -v 2>&1 | tee results/guard_tests.txt
"$GUARD_PY" -m coverage report | tee results/guard_coverage.txt
"$GUARD_PY" -m coverage json -o results/guard_coverage.json
"$GUARD_PY" -m src.benchmark_guard | tee results/guard_run.txt
"$GUARD_PY" scripts_notebook_guard.py
