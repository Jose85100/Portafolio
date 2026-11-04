"""Reproduce the dependent-variance experiment and write auditable outputs."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy

from .dependent_interval import (
    gls_chisquare_interval,
    iid_chisquare_interval,
    paired_chebyshev_interval,
    pair_variance_coefficient,
)
from .variance_interval import wilson_interval


def _stationary_ar1(rng: np.random.Generator, n: int, rho: float, variance: float) -> np.ndarray:
    x = np.empty(n, dtype=np.float64)
    x[0] = rng.normal(0.0, np.sqrt(variance))
    innovations = rng.normal(0.0, np.sqrt(variance * (1.0 - rho * rho)), n - 1)
    for i in range(1, n):
        x[i] = rho * x[i - 1] + innovations[i - 1]
    return x


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / "dependent-config.json").read_text())
    samples: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    for seed in config["seeds"]:
        rng = np.random.default_rng(seed)
        for n in config["n"]:
            for rho in config["rho"]:
                for repetition in range(config["repetitions_per_seed_cell"]):
                    truth = 1.0
                    x = _stationary_ar1(rng, n, rho, truth)
                    sample_id = len(samples)
                    samples.append({"sample_id": sample_id, "seed": seed, "n": n, "rho": rho, "repetition": repetition, "variance": truth})
                    estimates = [
                    iid_chisquare_interval(x.tolist(), config["confidence"]),
                    paired_chebyshev_interval(x.tolist(), rho, config["confidence"]),
                    gls_chisquare_interval(x.tolist(), rho, config["confidence"]),
                    ]
                    raw_pair = float(np.mean(np.diff(x) ** 2) / 2.0)
                    corrected_pair = raw_pair / (1.0 - rho)
                    results.extend(
                        {
                            "sample_id": sample_id,
                            "seed": seed,
                            "n": n,
                            "rho": rho,
                            "repetition": repetition,
                            "method": estimate.method,
                            "estimate": estimate.estimate,
                            "low": estimate.low,
                            "high": estimate.high,
                            "abstained": int(estimate.abstained),
                        "covered": int(estimate.low is not None and estimate.high is not None and estimate.low <= truth <= estimate.high),
                            "raw_pair_mean": raw_pair,
                            "corrected_pair_estimate": corrected_pair,
                        }
                        for estimate in estimates
                    )

    aggregates: list[dict[str, Any]] = []
    for n in config["n"]:
        for rho in config["rho"]:
            for method in ("iid_chisquare", "paired_chebyshev", "gls_chisquare"):
                subset = [r for r in results if r["n"] == n and r["rho"] == rho and r["method"] == method]
                successes = sum(int(r["covered"]) for r in subset)
                low, high = wilson_interval(successes, len(subset))
                aggregates.append({
                    "n": n, "rho": rho, "method": method, "trials": len(subset),
                    "coverage": successes / len(subset), "coverage_wilson_low": low,
                    "coverage_wilson_high": high,
                    "mean_estimate": float(np.mean([r["estimate"] for r in subset])),
                    "mean_absolute_error": float(np.mean([abs(r["estimate"] - 1.0) for r in subset])),
                    "mean_interval_width": float(np.mean([r["high"] - r["low"] for r in subset if r["low"] is not None])),
                    "abstentions": sum(int(r["abstained"]) for r in subset),
                })

    out = root / "results"
    _write_csv(out / "dependent-samples.csv", samples)
    _write_csv(out / "dependent-interval.csv", results)
    _write_csv(out / "dependent-aggregate.csv", aggregates)

    threshold = float(config["threshold"])
    gls_rows = [r for r in aggregates if r["method"] == "gls_chisquare"]
    threshold_failures = [r for r in gls_rows if r["coverage_wilson_low"] < threshold]
    # Runtime is isolated to estimator calls; sample generation and imports are excluded.
    runtime: list[dict[str, Any]] = []
    x_bench = _stationary_ar1(np.random.default_rng(42), 256, 0.9, 1.0)
    for method in ("paired_chebyshev", "gls_chisquare"):
        for repetition in range(30):
            tracemalloc.start()
            start = time.perf_counter()
            estimate = (paired_chebyshev_interval(x_bench.tolist(), 0.9) if method == "paired_chebyshev"
                        else gls_chisquare_interval(x_bench.tolist(), 0.9))
            elapsed = time.perf_counter() - start
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            runtime.append({"n": len(x_bench), "rho": 0.9, "method": method,
                            "repetition": repetition, "seconds": elapsed,
                            "python_peak_bytes": peak, "estimate": estimate.estimate})
    _write_csv(out / "dependent-runtime.csv", runtime)

    # Sensitivity surface is illustrative, not fit to data.
    surface = []
    for n in (32, 64, 128, 256, 512):
        for rho in np.linspace(-0.5, 0.98, 75):
            coefficient = pair_variance_coefficient(n, float(rho))
            surface.append({"n": n, "rho": float(rho), "relative_variance_coefficient": coefficient,
                            "chebyshev_epsilon": float(np.sqrt(coefficient / (1.0 - config["confidence"])))})
    _write_csv(out / "dependent-sensitivity.csv", surface)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), layout="constrained")
    colors = {"iid_chisquare": "#D55E00", "paired_chebyshev": "#009E73", "gls_chisquare": "#0072B2"}
    markers = {"iid_chisquare": "s", "paired_chebyshev": "^", "gls_chisquare": "o"}
    for method, color in colors.items():
        for n, linestyle in ((64, "--"), (256, "-")):
            points = [r for r in aggregates if r["method"] == method and r["n"] == n]
            points.sort(key=lambda r: float(r["rho"]))
            axes[0].errorbar([r["rho"] for r in points], [r["coverage"] for r in points],
                yerr=[[r["coverage"] - r["coverage_wilson_low"] for r in points],
                      [r["coverage_wilson_high"] - r["coverage"] for r in points]],
                color=color, marker=markers[method], linestyle=linestyle, capsize=2,
                label=f"{method}; n={n}")
    axes[0].axhline(config["confidence"], color="black", linestyle=":", label="90% nominal")
    axes[0].axhline(threshold, color="gray", linestyle="--", label="H1 screen=80% Wilson low")
    axes[0].set(xlabel="Known AR(1) persistence rho", ylabel="Coverage (Wilson 95% interval)", ylim=(0.0, 1.02),
                title="Synthetic AR(1): interval coverage")
    axes[0].legend(fontsize=6, ncol=2)
    for n in (32, 64, 128, 256, 512):
        points = [r for r in surface if r["n"] == n]
        axes[1].plot([r["rho"] for r in points], [r["chebyshev_epsilon"] for r in points], label=f"n={n}")
    axes[1].axhline(1, color="black", linestyle="--", label="abstention boundary")
    axes[1].set(xlabel="Known AR(1) persistence rho", ylabel="Relative Chebyshev radius epsilon",
                title="Conservatism and abstention sensitivity")
    axes[1].legend(fontsize=7)
    fig.suptitle("Stationary Gaussian simulation only; known rho, unknown mean and variance")
    fig.savefig(out / "dependent-interval.png", dpi=160)

    summary = {
        "config": config, "samples": len(samples), "estimator_rows": len(results),
        "threshold_failures_for_gls_h1": threshold_failures,
        "h1_screen_pass": not threshold_failures,
        "gls_min_cell_wilson_low": min(r["coverage_wilson_low"] for r in gls_rows),
        "paired_min_cell_wilson_low": min(r["coverage_wilson_low"] for r in aggregates if r["method"] == "paired_chebyshev"),
        "hardware": platform.platform(), "python": sys.version,
        "versions": {"numpy": np.__version__, "scipy": scipy.__version__, "matplotlib": matplotlib.__version__},
        "config_sha256": hashlib.sha256((root / "dependent-config.json").read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256((Path(__file__).with_name("dependent_interval.py")).read_bytes()).hexdigest(),
        "data_status": "synthetic; not empirical evidence",
    }
    (out / "dependent-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
