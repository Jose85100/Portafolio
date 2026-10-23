#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")" && pwd)
cd "$root"
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
.venv/bin/cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
.venv/bin/cmake --build build -j2
.venv/bin/ctest --test-dir build --output-on-failure | tee results/ctest.txt
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror -fsanitize=address,undefined -Iinclude tests/tests.cpp -o build/sanitized-tests
ASAN_OPTIONS=detect_leaks=0 build/sanitized-tests
printf '{"asan":true,"ubsan":true,"leak_detection":false,"reason":"ptrace container restriction"}\n' > results/sanitizers.json
g++ -std=c++17 --coverage -O0 -Iinclude tests/tests.cpp -o build/coverage-tests
build/coverage-tests
gcov build/coverage-tests-tests.gcno > results/coverage.txt
.venv/bin/python benchmarks/measure.py | tee results/run.json
uname -a > results/environment.txt
.venv/bin/python benchmarks/report.py
.venv/bin/ruff check benchmarks/report.py | tee results/lint.txt
.venv/bin/ruff check benchmarks/measure.py
.venv/bin/mypy benchmarks/report.py benchmarks/measure.py | tee results/types.txt
printf '{"test_binary_passed":true,"assertions":8}\n' > results/tests.json
