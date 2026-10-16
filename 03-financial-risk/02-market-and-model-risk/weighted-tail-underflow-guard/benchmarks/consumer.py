"""Decision/transport audit using original fixture inputs and independent oracle."""

import hashlib
import json
import platform
import random
import statistics
import time
import tracemalloc
from fractions import Fraction
from pathlib import Path
from typing import Any

from benchmarks.run import write_csv
from src.consumer import decide, encode
from src.guard import guarded_tail
from src.sources import oracle

PROJECT = Path(__file__).resolve().parents[1]


def main() -> None:
    results = PROJECT / "results"
    cases = json.loads((results / "fixtures.json").read_text())
    rows: list[dict[str, Any]] = []
    for i, c in enumerate(cases):
        ref: Fraction = oracle.exact_es(c["losses"], c["weights"], c["alpha"])
        r = guarded_tail(c["losses"], c["alpha"], c["weights"])
        # Zero threshold isolates sign loss, not near-boundary general rounding.
        packet = decide(c["losses"], "0", c["alpha"], c["weights"])
        payload = encode(packet)
        restored = json.loads(payload)
        assert restored == packet
        truth = ref > 0
        rows.append(
            {
                "id": i,
                "label": c["label"],
                "reference_positive": truth,
                "naive_breach": r.es > 0,
                "contract_breach": packet["breach"],
                "naive_error": (r.es > 0) != truth,
                "contract_error": packet["breach"] != truth,
                "comparison_basis": packet["comparison_basis"],
                "payload_bytes": len(payload),
            }
        )
    assert not any(r["contract_error"] for r in rows)
    write_csv(results / "consumer-accuracy.csv", rows)
    timing: list[dict[str, Any]] = []
    rng = random.Random(20261016)
    for n in [2, 32, 256, 2048]:
        for regime in ["ordinary", "tiny_weight"]:
            x = [1.0] * n if regime == "ordinary" else [5e-324] + [0.0] * (n - 1)
            w = [1.0] * n if regime == "ordinary" else [1.0] + [3.0] * (n - 1)
            methods = {
                "naive_guard_float": lambda: guarded_tail(x, 0.5, w).es > 0,
                "contract_json": lambda: encode(decide(x, "0", 0.5, w)),
            }
            for fn in methods.values():
                fn()
            for rep in range(7):
                order = list(methods)
                rng.shuffle(order)
                for position, name in enumerate(order):
                    start = time.perf_counter_ns()
                    methods[name]()
                    elapsed = time.perf_counter_ns() - start
                    tracemalloc.start()
                    methods[name]()
                    _, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    timing.append(
                        {
                            "n": n,
                            "regime": regime,
                            "rep": rep,
                            "order": position,
                            "method": name,
                            "nanoseconds": elapsed,
                            "allocated_peak_bytes": peak,
                        }
                    )
    write_csv(results / "consumer-performance.csv", timing)
    rejected = decide([1e308, 0], "0", weights=[1e-300, 1e300], policy="raise")
    capped = decide([1e308, 0], "0", weights=[1e-300, 1e300], max_exact_scenarios=1)
    assert rejected["breach"] is None and capped["breach"] is None
    summary = {
        "date": "2026-10-16",
        "seed": 20261016,
        "threshold": "0",
        "fixtures": len(rows),
        "naive_errors": sum(r["naive_error"] for r in rows),
        "contract_errors": sum(r["contract_error"] for r in rows),
        "rejection_policies_checked": 2,
        "performance_rows": len(timing),
        "python": platform.python_version(),
        "source_sha256": {
            name: hashlib.sha256((PROJECT / name).read_bytes()).hexdigest()
            for name in ["src/consumer.py", "src/guard.py", "benchmarks/consumer.py", "results/fixtures.json"]
        },
        "cpu": json.loads((results / "metadata.json").read_text())["cpu"],
        "platform": platform.platform(),
        "medians_ms": {
            f"{n}/{regime}/{method}": statistics.median(
                r["nanoseconds"]
                for r in timing
                if r["n"] == n and r["regime"] == regime and r["method"] == method
            )
            / 1e6
            for n in [2, 32, 256, 2048]
            for regime in ["ordinary", "tiny_weight"]
            for method in ["naive_guard_float", "contract_json"]
        },
    }
    (results / "consumer-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (results / "consumer-examples.json").write_text(
        json.dumps(
            {
                "nonrepresentable": decide([0, 5e-324], "0", 0.5, [3, 1]),
                "policy_rejection": rejected,
                "budget_rejection": capped,
            },
            indent=2,
            allow_nan=False,
        )
        + "\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
