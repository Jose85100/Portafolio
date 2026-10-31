"""Deterministic scenarios; Decimal oracle, fair offline scaled NumPy baseline."""

import csv
import json
import math
import platform
import time
import tracemalloc
import warnings
from pathlib import Path
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.dynamic import dynamic_moments
from src.scaled import scaled_moments
from decimal import Decimal, localcontext


def oracle(values: list[float]) -> float:
    with localcontext() as ctx:
        ctx.prec = 100
        xs = [Decimal(x) for x in values]
        mean = sum(xs) / len(xs)
        return float((sum((x - mean) ** 2 for x in xs) / len(xs)).sqrt())


def main() -> None:
    config = json.loads(Path("config_dynamic.json").read_text())
    rows = []
    for seed in config["seeds"]:
        rng = np.random.default_rng(seed)
        for exponent in config["exponents"]:
            base = rng.uniform(-1, 1, config["n"])
            xs = [math.ldexp(float(x), exponent) for x in base]
            for order, values in [
                ("original", xs),
                ("reverse", xs[::-1]),
                ("sorted", sorted(xs)),
            ]:
                expected = oracle(values)
                e = max(math.frexp(x)[1] for x in values if x)

                def offline():
                    return math.ldexp(
                        float(np.std([math.ldexp(x, -e) for x in values])), e
                    )

                methods = {
                    "dynamic": lambda: dynamic_moments(iter(values)).std,
                    "numpy_scaled": offline,
                    "external_zero": lambda: scaled_moments(iter(values), 0).std,
                }
                for name, fn in methods.items():
                    timings = []
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        for _ in range(config["repeats"]):
                            start = time.perf_counter_ns()
                            answer = fn()
                            timings.append(time.perf_counter_ns() - start)
                        tracemalloc.start()
                        fn()
                        _, peak = tracemalloc.get_traced_memory()
                        tracemalloc.stop()
                    error = (
                        abs(answer - expected) / expected
                        if answer is not None and expected
                        else None
                    )
                    rows.append(
                        dict(
                            seed=seed,
                            exponent=exponent,
                            order=order,
                            method=name,
                            n=len(values),
                            sd=answer,
                            oracle_sd=expected,
                            relative_error=error,
                            median_ns=float(np.median(timings)),
                            peak_python_bytes=peak,
                        )
                    )
    with Path("results/dynamic_raw.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    dynamic = [r for r in rows if r["method"] == "dynamic"]
    summary = {
        "cases": len(dynamic),
        "max_relative_error": max(r["relative_error"] for r in dynamic),
        "gate": all(r["relative_error"] <= 1e-12 for r in dynamic),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "hardware": platform.processor(),
        "timing_scope": "compute+input normalization only; imports/install excluded; 5 repeats; tracemalloc separate, Python heap not RSS",
        "median_ns": {
            m: float(np.median([r["median_ns"] for r in rows if r["method"] == m]))
            for m in ["dynamic", "numpy_scaled"]
        },
    }
    Path("results/dynamic_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for method, marker in [("dynamic", "o"), ("numpy_scaled", "x")]:
        sample = [r for r in rows if r["method"] == method]
        axes[0].scatter(
            [r["exponent"] for r in sample],
            [max(r["relative_error"], 1e-18) for r in sample],
            label=method,
            marker=marker,
            alpha=0.5,
        )
    axes[0].set_yscale("log")
    axes[0].set_xlabel("Binary input exponent (dimensionless)")
    axes[0].set_ylabel("Relative SD error vs Decimal100")
    axes[0].legend()
    axes[0].set_title("3 seeds × 3 stream orders; n=128")
    axes[1].bar(
        list(summary["median_ns"]),
        [v / 1000 for v in summary["median_ns"].values()],
        color=["#0072B2", "#D55E00"],
    )
    axes[1].set_ylabel("Median compute time (microseconds)")
    axes[1].set_title("Offline NumPy may inspect all data first")
    fig.suptitle("Synthetic binary64 inputs; zero error drawn at 1e-18 for log axis", fontsize=10)
    fig.tight_layout()
    fig.savefig("results/dynamic_audit.png", dpi=150)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
