#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
MATH_ENV="${MATH_ENV:-$PWD/.venv-joint}"
python -m venv "$MATH_ENV"
"$MATH_ENV/bin/python" -m pip install -r requirements.txt --quiet
chmod u+x "$MATH_ENV/bin/ruff"
MATH_PY="$MATH_ENV/bin/python"
"$MATH_PY" -m ruff check src/joint_gate.py src/benchmark_joint.py tests/test_joint_gate.py scripts_notebook_joint.py
"$MATH_PY" -m mypy src/joint_gate.py src/benchmark_joint.py --ignore-missing-imports
"$MATH_PY" -m coverage run --source=src.joint_gate -m unittest discover -s tests -v 2>&1 | tee results/joint_tests.txt
"$MATH_PY" -m coverage report | tee results/joint_coverage.txt
"$MATH_PY" -m coverage json -o results/joint_coverage.json
"$MATH_PY" -m src.benchmark_joint | tee results/joint_run.txt
"$MATH_PY" scripts_notebook_joint.py
