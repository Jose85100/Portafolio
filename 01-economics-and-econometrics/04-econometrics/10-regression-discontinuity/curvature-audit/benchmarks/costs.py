"""Per-arm instrumented runtime/memory; simulation excluded from measurement."""

import csv
import time
import tracemalloc
from pathlib import Path
from src.rd import estimate, sample


def run():
    rows = []
    for n in [120, 1200, 12000]:
        x, y = sample(20261025, n)
        for h in [1.0, 0.4, 0.2]:
            start = time.perf_counter()
            tracemalloc.start()
            for _ in range(100):
                estimate(x, y, h, min_side=2)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            rows.append(
                {
                    "n": n,
                    "h": h,
                    "calls": 100,
                    "seconds": time.perf_counter() - start,
                    "python_peak_bytes": peak,
                }
            )
    with (Path(__file__).resolve().parents[1] / "results/costs.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(rows)


if __name__ == "__main__":
    run()
