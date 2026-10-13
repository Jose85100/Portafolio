"""Execute all configured independent replications and retain raw evidence."""

from dataclasses import asdict
import csv
import json
import platform
from pathlib import Path
import sys
import time
import tracemalloc
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.estimators import estimate, population_variance, truth

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    config = json.loads((ROOT / "config.json").read_text())
    rows, summary = [], []
    for ai, a in enumerate(config["thresholds"]):
        exact = truth(a)
        for ni, n in enumerate(config["sample_sizes"]):
            for mi, method in enumerate(config["methods"]):
                group = []
                for r in range(config["replications"]):
                    seed = config["base_seed"] + ai * 100000 + ni * 10000 + mi * 1000 + r
                    start = time.perf_counter()
                    result = estimate(a, n, seed, method)
                    row = dict(
                        a=a,
                        n=n,
                        method=method,
                        replicate=r,
                        seed=seed,
                        truth=exact,
                        seconds=time.perf_counter() - start,
                        **asdict(result),
                    )
                    row["covered_95"] = abs(result.mean - exact) <= 1.96 * result.se
                    row["zero_estimate"] = result.mean == 0
                    rows.append(row)
                    group.append(row)
                errors = np.array([row["mean"] - exact for row in group])
                # Memory profiling separate from timings; NumPy allocations captured
                # by tracemalloc, not whole-process RSS or allocator peak.
                tracemalloc.start()
                estimate(a, n, config["base_seed"], method)
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                var = population_variance(a, method)
                summary.append(
                    dict(
                        a=a,
                        n=n,
                        method=method,
                        truth=exact,
                        mean=float(np.mean([row["mean"] for row in group])),
                        rmse=float(np.sqrt(np.mean(errors**2))),
                        relative_rmse=float(np.sqrt(np.mean(errors**2)) / exact),
                        bias=float(np.mean(errors)),
                        coverage_95=float(np.mean([row["covered_95"] for row in group])),
                        zero_fraction=float(np.mean([row["zero_estimate"] for row in group])),
                        missing_left_fraction=float(
                            np.mean([row["left_hits"] == 0 for row in group])
                        ),
                        median_seconds=float(np.median([row["seconds"] for row in group])),
                        traced_peak_bytes=peak,
                        population_variance_per_draw=var,
                        theoretical_relative_se=float(np.sqrt(var / n) / exact),
                    )
                )
    out = ROOT / "benchmarks"
    for name, data in [("raw.csv", rows), ("summary.csv", summary)]:
        with (out / name).open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(data)
    gate = config["success_gate"]
    selected = {
        row["method"]: row
        for row in summary
        if row["a"] == gate["threshold"] and row["n"] == gate["sample_size"]
    }
    ratio = selected["balanced"]["rmse"] / selected["direct"]["rmse"]
    success = (
        ratio <= gate["max_rmse_ratio_balanced_to_direct"]
        and selected["balanced"]["relative_rmse"] <= gate["max_relative_rmse_balanced"]
    )
    report = dict(
        success=success,
        rmse_ratio=ratio,
        selected=selected,
        environment=dict(
            python=sys.version,
            platform=platform.platform(),
            processor=platform.processor(),
            numpy=np.__version__,
        ),
        note="40 replications; Wald intervals are diagnostic, not guaranteed calibrated",
    )
    (out / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    fig, ax = plt.subplots(figsize=(8, 5))
    for method in config["methods"]:
        data = [row for row in summary if row["method"] == method and row["n"] == 20000]
        ax.semilogy(
            [row["a"] for row in data], [row["relative_rmse"] for row in data], "o-", label=method
        )
    ax.set(
        xlabel="Threshold a",
        ylabel="Empirical relative RMSE (40 replications)",
        title="Disconnected Gaussian tails: finite-sample audit",
    )
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "rmse.png", dpi=150)
    plt.close(fig)
    print(json.dumps({"success": success, "rmse_ratio": ratio, "selected": selected}, indent=2))
    if not success:
        raise RuntimeError("Predeclared success gate failed; retain outputs and report failure")


if __name__ == "__main__":
    main()
