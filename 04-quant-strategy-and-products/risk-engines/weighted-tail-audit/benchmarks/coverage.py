"""Preserve gcov raw JSON and report line coverage of only weighted_tail.hpp."""

import gzip
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
results = root / "results"
gcno = root / "build/coverage/CMakeFiles/weighted_tail_tests.dir/tests/test_weighted.cpp.gcno"
output = subprocess.check_output(
    ["gcov", "--json-format", "--branch-probabilities", "--branch-counts", str(gcno)], cwd=results, text=True
)
(results / "gcov.txt").write_text(output)
raw = json.loads(gzip.decompress((results / "test_weighted.cpp.gcov.json.gz").read_bytes()))
files = [file for file in raw["files"] if file["file"].endswith("/quant/weighted_tail.hpp")]
assert len(files) == 1, "weighted header absent from coverage"
lines = files[0]["lines"]
covered = sum(line["count"] > 0 for line in lines)
summary = {
    "scope": "weighted_tail.hpp line coverage only; compiler-generated branches excluded",
    "covered_lines": covered,
    "executable_lines": len(lines),
    "line_percent": covered * 100 / len(lines),
    "uncovered": [line["line_number"] for line in lines if line["count"] == 0],
    "gcc_version": raw["gcc_version"],
}
(results / "coverage.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
