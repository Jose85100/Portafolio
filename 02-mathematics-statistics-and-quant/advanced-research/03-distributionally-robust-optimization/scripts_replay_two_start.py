"""Reconstruct per-case evidence for the failed two-start baseline, with fresh timings."""

from collections import Counter
import csv
import json
from pathlib import Path
import time
import warnings
import numpy as np
from src.benchmark import dataset
from src.kl_robust import robust_expectation
from src.reference import slsqp_reference

ROOT = Path(__file__).resolve().parent
config = json.loads((ROOT / "config.json").read_text())
rows = []
for n in config["sizes"]:
    for family in config["loss_families"]:
        for seed in config["seeds"]:
            p, loss = dataset(n, seed, family)
            for radius in config["radii"]:
                target = robust_expectation(p, loss, radius)
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    start = time.perf_counter()
                    result = slsqp_reference(p, loss, radius, variant="two_start")
                    seconds = time.perf_counter() - start
                rows.append(
                    dict(
                        n=n,
                        family=family,
                        seed=seed,
                        radius=radius,
                        robust=target.value,
                        slsqp_value=result.value,
                        scaled_difference=abs(result.value - target.value)
                        / max(1.0, float(np.ptp(loss))),
                        slsqp_success=result.success,
                        slsqp_kl=result.divergence,
                        mass_error=result.mass_error,
                        message=result.message,
                        iterations=result.iterations,
                        replay_seconds=seconds,
                        warning_counts=json.dumps(dict(Counter(str(w.message) for w in caught))),
                    )
                )
output = ROOT / "benchmarks/two_start_baseline/replayed_raw.csv"
with output.open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
print(
    "Replayed", len(rows), "cases; max scaled error", max(row["scaled_difference"] for row in rows)
)
