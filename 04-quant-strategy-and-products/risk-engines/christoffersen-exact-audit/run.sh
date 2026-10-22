#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -c 'import sys; assert sys.platform == "linux"; assert sys.version_info[:2] == (3,12)'
python3 -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt
mkdir -p build results
export PATH="$PWD/.venv/bin:$PATH"
ruff check benchmarks | tee results/lint.txt
ruff format --check benchmarks | tee results/format.txt
mypy benchmarks | tee results/types.txt
clang-format --dry-run --Werror include/exact.hpp src/main.cpp tests/tests.cpp
if command -v clang-tidy >/dev/null; then
  clang-tidy --warnings-as-errors='*' src/main.cpp tests/tests.cpp -- -std=c++17 -Iinclude 2>&1 | tee results/clang-tidy.txt
else
  echo "clang-tidy unavailable; strict g++ warnings remain enforced" | tee results/clang-tidy.txt
fi
cmake -S . -B build/cmake -DCMAKE_BUILD_TYPE=Release
cmake --build build/cmake --parallel 2
ctest --test-dir build/cmake --output-on-failure | tee results/ctest.txt
flags=(-std=c++17 -Wall -Wextra -Wpedantic -Wconversion -Werror -Iinclude)
g++ "${flags[@]}" -O2 src/main.cpp -o build/exact_audit
g++ "${flags[@]}" -O2 tests/tests.cpp -o build/exact_tests
build/exact_tests | tee results/tests.json
export ASAN_OPTIONS="${ASAN_OPTIONS:-detect_leaks=0}"
g++ "${flags[@]}" -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -no-pie tests/tests.cpp -o build/tests_sanitized
build/tests_sanitized | tee results/sanitizers.json
g++ "${flags[@]}" -O0 --coverage -fprofile-abs-path tests/tests.cpp -o build/tests_coverage
build/tests_coverage > results/coverage-tests.json
(cd build && gcov -b -c tests_coverage-tests.gcno) > results/coverage.txt
.venv/bin/python benchmarks/report.py | tee results/run.stdout.json
