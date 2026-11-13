"""Output contract checks; fail closed on missing or malformed artifacts."""
import csv
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root / "results"
required = ["summary.json", "ablation.json", "monte_carlo_check.json", "numerical_audit.json",
            "delay_sensitivity.csv", "prior_sensitivity.csv", "benchmark.csv", "delay_frontier.png"]
missing = [p for p in required if not (out/p).is_file() or (out/p).stat().st_size == 0]
assert not missing, f"missing outputs: {missing}"
summary = json.loads((out/"summary.json").read_text())
assert summary["synthetic"] is True
assert len(list(csv.DictReader((out/"delay_sensitivity.csv").open()))) == 9
notebook = json.loads((root/"notebook.ipynb").read_text())
assert len(notebook["cells"]) >= 5 and all(c.get("execution_count") for c in notebook["cells"] if c["cell_type"] == "code")
print(f"PASS: {len(required)} required results; synthetic-only provenance")
