#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON=${PYTHON:-python3}
"$PYTHON" -m unittest tests.test_delta_replay -v 2>&1 | tee results/delta1104/tests.txt
"$PYTHON" -m ruff check src/delta_replay.py tests/test_delta_replay.py benchmarks/delta_experiment.py 2>&1 | tee results/delta1104/lint.txt
"$PYTHON" -m mypy src/delta_replay.py --strict 2>&1 | tee results/delta1104/types.txt
"$PYTHON" -m benchmarks.delta_experiment | tee results/delta1104/run.log
"$PYTHON" benchmarks/execute_notebook.py notebook_delta1104.ipynb
"$PYTHON" -c 'import json,platform; from pathlib import Path; Path("results/delta1104/environment.json").write_text(json.dumps({"python":platform.python_version(),"platform":platform.platform()},indent=2)+"\n")'
