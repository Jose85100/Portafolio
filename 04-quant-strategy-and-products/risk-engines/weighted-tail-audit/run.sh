#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -c 'import sys; assert sys.version_info[:2] == (3,12), "Requires Python 3.12"; assert sys.platform == "linux", "Requires Linux"'
command -v g++ >/dev/null
command -v gcov >/dev/null
python3 -m venv .venv
export PATH="$PWD/.venv/bin:$PATH"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
# LeakSanitizer requires /proc/ptrace unavailable in some managed runtimes.
# Address/undefined checks stay enabled. Set ASAN_OPTIONS=detect_leaks=1 externally
# where supported; the CI job does so. Do not claim local leak verification.
export ASAN_OPTIONS="${ASAN_OPTIONS:-detect_leaks=0}"
python -m pip install --disable-pip-version-check -r requirements.txt
mkdir -p results
ruff check benchmarks tests | tee results/python-lint.txt
ruff format --check benchmarks tests | tee results/python-format.txt
mypy benchmarks tests | tee results/python-types.txt
clang-format --dry-run --Werror src/main.cpp tests/test_weighted.cpp ../include/quant/weighted_tail.hpp
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure | tee results/ctest-release.txt
build/release/weighted_tail_tests | tee results/checks.json
python -m unittest discover -s tests -p 'test_*.py' -v 2>&1 | tee results/python-tests.txt
clang-tidy -p build/release src/main.cpp tests/test_weighted.cpp 2>&1 | tee results/clang-tidy.txt
python benchmarks/audit.py | tee results/run.json
cmake -S . -B build/sanitized -DCMAKE_BUILD_TYPE=Debug -DAUDIT_SANITIZERS=ON
cmake --build build/sanitized --parallel 2
ctest --test-dir build/sanitized --output-on-failure | tee results/ctest-sanitized.txt
build/sanitized/weighted_tail_cli --fixtures results/fixtures.txt > results/sanitized-fixtures.csv
for mode in weighted expanded uniform_ablation; do
  build/sanitized/weighted_tail_cli --bench "$mode" 1000 1 20261014 --csv > "results/sanitized-${mode}.csv"
done
cmake -S . -B build/coverage -DCMAKE_BUILD_TYPE=Debug -DAUDIT_COVERAGE=ON
cmake --build build/coverage --parallel 2
ctest --test-dir build/coverage --output-on-failure | tee results/ctest-coverage.txt
python benchmarks/coverage.py | tee results/coverage-summary.txt
cmake -S .. -B build/legacy -DCMAKE_BUILD_TYPE=Debug
cmake --build build/legacy --parallel 2
ctest --test-dir build/legacy --output-on-failure | tee results/ctest-legacy.txt
