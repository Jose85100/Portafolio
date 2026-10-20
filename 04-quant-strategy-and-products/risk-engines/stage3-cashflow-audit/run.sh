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
mypy --ignore-missing-imports benchmarks | tee results/types.txt
clang-format --dry-run --Werror src/main.cpp tests/tests.cpp ../include/quant/stage3.hpp
clang-tidy --warnings-as-errors='*' src/main.cpp tests/tests.cpp -- -std=c++17 -I../include 2>&1 | tee results/clang-tidy.txt
cmake -S . -B build/cmake -DCMAKE_BUILD_TYPE=Release
cmake --build build/cmake --parallel 2
ctest --test-dir build/cmake --output-on-failure | tee results/ctest.txt
cmake -S .. -B build/legacy -DCMAKE_BUILD_TYPE=Release
cmake --build build/legacy --parallel 2
ctest --test-dir build/legacy --output-on-failure | tee results/ctest-legacy.txt
flags=(-std=c++17 -Wall -Wextra -Wpedantic -Wconversion -Werror -I../include)
g++ "${flags[@]}" -O2 src/main.cpp -o build/stage3_cli
g++ "${flags[@]}" -O2 tests/tests.cpp -o build/stage3_tests
build/stage3_tests | tee results/tests.json
export ASAN_OPTIONS="${ASAN_OPTIONS:-detect_leaks=0}"
g++ "${flags[@]}" -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -no-pie tests/tests.cpp -o build/tests_sanitized
g++ "${flags[@]}" -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -no-pie src/main.cpp -o build/stage3_sanitized
build/tests_sanitized | tee results/sanitized-tests.json
# Compile coverage separately: optimization and sanitizers must not distort coverage.
if [[ -f build/tests_coverage-tests.gcda ]]; then
  rm -- build/tests_coverage-tests.gcda
fi
g++ "${flags[@]}" -O0 --coverage -fprofile-abs-path tests/tests.cpp -o build/tests_coverage
build/tests_coverage > results/coverage-tests.json
(cd build && gcov -b -c tests_coverage-tests.gcno) > results/coverage.txt
.venv/bin/python benchmarks/audit.py | tee results/run.json
