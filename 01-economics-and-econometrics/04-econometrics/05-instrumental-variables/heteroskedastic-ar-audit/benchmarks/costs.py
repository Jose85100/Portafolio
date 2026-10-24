"""Instrumented cost of each comparable test; generation excluded."""

import csv
import time
import tracemalloc
from pathlib import Path
from src.baseline import ar_pvalue
from src.robust import robust_ar, sample


def run():
    rows = []
    for n in [100, 1000, 10000]:
        data = sample(20261024, n, True)
        for name, method in [
            ("F", ar_pvalue),
            ("HC1", lambda *args: robust_ar(*args, kind="HC1")),
            ("HC3", robust_ar),
        ]:
            start = time.perf_counter()
            tracemalloc.start()
            for _ in range(100):
                method(*data, 1)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            rows.append(
                {
                    "n": n,
                    "method": name,
                    "calls": 100,
                    "seconds": time.perf_counter() - start,
                    "python_peak_bytes": peak,
                }
            )
    with (Path(__file__).resolve().parents[1] / "results/costs.csv").open("w") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(rows)


if __name__ == "__main__":
    run()
