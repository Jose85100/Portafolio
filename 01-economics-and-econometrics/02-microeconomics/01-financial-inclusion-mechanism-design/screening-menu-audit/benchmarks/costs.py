"""Independent cost comparison on identical economies, generation excluded."""

import csv
import time
import tracemalloc
from pathlib import Path
import numpy as np
from src.screening import Economy, analytic, qp


def run():
    rng = np.random.default_rng(20261026)
    economies = []
    for _ in range(50):
        low = rng.uniform(0.5, 2)
        economies.append(
            Economy(
                low,
                low + rng.uniform(0.2, 2),
                rng.uniform(0.05, 0.95),
                rng.uniform(0.5, 2),
            )
        )
    rows = []
    for count in [1, 10, 50]:
        for name, method in [("closed_form", analytic), ("numerical_QP", qp)]:
            start = time.perf_counter()
            tracemalloc.start()
            for _ in range(3):
                for economy in economies[:count]:
                    method(economy)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            rows.append(
                {
                    "economies": count,
                    "calls": count * 3,
                    "method": name,
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
