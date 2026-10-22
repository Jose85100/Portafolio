#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m unittest tests.test_consensus -v
python3 -m benchmarks.run
python3 -m benchmarks.notebook
python3 -m unittest tests.test_artifacts -v
