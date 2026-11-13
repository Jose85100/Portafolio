"""Per-method scale audit; no throughput extrapolation or production claim."""

import csv
import time
import tracemalloc
from pathlib import Path
from src.inference import ar_pvalue, sample, wald_pvalue


def run():
    rows = []
    for n in (100, 1000, 10000):
        for name, method in [("AR", ar_pvalue), ("Wald", wald_pvalue)]:
            data = sample(20261023, n, 1)
            start = time.perf_counter()
            tracemalloc.start()
            for _ in range(100):
                method(*data, 1)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            rows.append(
                dict(
                    n=n,
                    method=name,
                    calls=100,
                    seconds=time.perf_counter() - start,
                    python_peak_bytes=peak,
                )
            )
    path = Path(__file__).resolve().parents[1] / "results/costs.csv"
    with path.open("w") as h:
        writer = csv.DictWriter(h, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(rows)


if __name__ == "__main__":
    run()
