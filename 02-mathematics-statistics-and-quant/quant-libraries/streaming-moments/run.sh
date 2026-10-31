#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
MATH_ENV=${MATH_ENV:-.venv}
if [ ! -x "$MATH_ENV/bin/python" ]; then python3 -m venv "$MATH_ENV"; fi
"$MATH_ENV/bin/python" -m pip install -q -r requirements.txt
chmod u+x "$MATH_ENV/bin/ruff"
"$MATH_ENV/bin/python" -m coverage run --source=src.moments,src.scaled,src.dynamic -m unittest discover -s tests -v 2>&1 | tee results/tests.txt
"$MATH_ENV/bin/python" -m coverage json -o results/coverage.json
"$MATH_ENV/bin/python" -m coverage report | tee results/coverage.txt
"$MATH_ENV/bin/ruff" check src tests scripts_notebook.py scripts_notebook_scale.py scripts_notebook_dynamic.py | tee results/lint.txt
"$MATH_ENV/bin/python" -m mypy src/moments.py src/scaled.py src/dynamic.py | tee results/types.txt
"$MATH_ENV/bin/python" -m src.benchmark > results/run.txt
"$MATH_ENV/bin/python" scripts_notebook.py
"$MATH_ENV/bin/python" -m src.benchmark_scale > results/scale_run.txt
"$MATH_ENV/bin/python" scripts_notebook_scale.py

"$MATH_ENV/bin/python" -m src.benchmark_dynamic > results/dynamic_run.txt
"$MATH_ENV/bin/python" scripts_notebook_dynamic.py
