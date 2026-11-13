#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
MATH_ENV=${MATH_ENV:-.venv}
if [ ! -x "$MATH_ENV/bin/python" ]; then python3 -m venv "$MATH_ENV"; fi
"$MATH_ENV/bin/python" -m pip install -q -r requirements.txt
chmod u+x "$MATH_ENV/bin/ruff"
"$MATH_ENV/bin/cmake" -S . -B .build -DCMAKE_BUILD_TYPE=Release > results/transport_build.txt
"$MATH_ENV/bin/cmake" --build .build -j2 >> results/transport_build.txt
"$MATH_ENV/bin/ctest" --test-dir .build --output-on-failure > results/transport_ctest.txt
"$MATH_ENV/bin/cmake" -S . -B .build-san -DCMAKE_BUILD_TYPE=Debug -DENABLE_SANITIZERS=ON > results/transport_sanitizers.txt
"$MATH_ENV/bin/cmake" --build .build-san -j2 >> results/transport_sanitizers.txt
ASAN_OPTIONS=detect_leaks=0 "$MATH_ENV/bin/ctest" --test-dir .build-san --output-on-failure >> results/transport_sanitizers.txt
"$MATH_ENV/bin/python" -m coverage run --source=src.moments,src.scaled,src.dynamic,src.transport,src.cpp_bridge,src.audit_envelope,src.reduction -m unittest discover -s tests -v 2>&1 | tee results/tests.txt
"$MATH_ENV/bin/python" -m coverage json -o results/coverage.json
"$MATH_ENV/bin/python" -m coverage report | tee results/coverage.txt
"$MATH_ENV/bin/ruff" check src tests scripts_notebook.py scripts_notebook_scale.py scripts_notebook_dynamic.py scripts_notebook_merge.py scripts_notebook_transport.py scripts_notebook_envelope.py scripts_notebook_reduction.py | tee results/lint.txt
"$MATH_ENV/bin/python" -m mypy src/moments.py src/scaled.py src/dynamic.py src/transport.py src/cpp_bridge.py src/audit_envelope.py src/benchmark_envelope.py src/reduction.py src/benchmark_reduction.py | tee results/types.txt
"$MATH_ENV/bin/python" -m src.benchmark > results/run.txt
"$MATH_ENV/bin/python" scripts_notebook.py
"$MATH_ENV/bin/python" -m src.benchmark_scale > results/scale_run.txt
"$MATH_ENV/bin/python" scripts_notebook_scale.py

"$MATH_ENV/bin/python" -m src.benchmark_dynamic > results/dynamic_run.txt
"$MATH_ENV/bin/python" scripts_notebook_dynamic.py

"$MATH_ENV/bin/python" -m src.benchmark_merge > results/merge_run.txt
"$MATH_ENV/bin/python" scripts_notebook_merge.py

"$MATH_ENV/bin/python" -m src.benchmark_transport > results/transport_run.txt
"$MATH_ENV/bin/python" scripts_notebook_transport.py

"$MATH_ENV/bin/python" -m src.benchmark_envelope > results/envelope_run.txt
"$MATH_ENV/bin/python" scripts_notebook_envelope.py

"$MATH_ENV/bin/python" -m unittest tests.test_reduction -v 2>&1 | tee results/reduction_tests.txt
"$MATH_ENV/bin/python" -m src.benchmark_reduction > results/reduction_run.txt
"$MATH_ENV/bin/python" scripts_notebook_reduction.py | tee results/reduction_notebook.txt
"$MATH_ENV/bin/ruff" check src/reduction.py src/benchmark_reduction.py tests/test_reduction.py scripts_notebook_reduction.py
"$MATH_ENV/bin/python" -m mypy src/reduction.py src/benchmark_reduction.py
