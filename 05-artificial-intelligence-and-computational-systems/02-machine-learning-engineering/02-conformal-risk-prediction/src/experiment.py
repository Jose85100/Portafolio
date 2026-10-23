"""Paired synthetic audit. Run python -m src.experiment from project root."""

from __future__ import annotations
import csv
import json
import platform
import resource
import time
import tracemalloc
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from src.conformal import ratios, thresholds


def run() -> dict:
    config = json.loads(Path("config.json").read_text())
    rows = []
    tracemalloc.start()
    start = time.perf_counter()
    for n in config["calibration_sizes"]:
        for scenario in ("no_shift", "covariate_shift", "conditional_shift"):
            target = (
                config["source_high"]
                if scenario == "no_shift"
                else config["target_high"]
            )
            for repeat in range(config["repeats"]):
                # Paired across methods; scenario streams are fixed independently.
                rng = np.random.default_rng(config["seed"] + repeat + n * 1000)
                g = rng.random(n) < config["source_high"]
                score = np.abs(rng.normal(size=n)) * np.where(g, 4.0, 1.0)
                gt = rng.random(config["test_size"]) < target
                residual = np.abs(rng.normal(size=len(gt))) * np.where(gt, 4.0, 1.0)
                if scenario == "conditional_shift":
                    residual *= 2  # violates the invariant conditional-law assumption
                w = ratios(g, config["source_high"], target)
                tw = ratios(gt, config["source_high"], target)
                ess = float(w.sum() ** 2 / np.square(w).sum())
                methods = {
                    "unweighted": thresholds(
                        score, np.ones(n), np.ones(len(gt)), config["alpha"]
                    ),
                    "naive_weighted": thresholds(score, w, tw, config["alpha"], False),
                    "correct_weighted": thresholds(score, w, tw, config["alpha"]),
                }
                for method, q in methods.items():
                    finite = np.isfinite(q)
                    rows.append(
                        dict(
                            n=n,
                            scenario=scenario,
                            repeat=repeat,
                            method=method,
                            coverage=float(np.mean(residual <= q)),
                            high_group_coverage=float(np.mean((residual <= q)[gt])),
                            finite_rate=float(finite.mean()),
                            finite_mean_width=float(2 * q[finite].mean())
                            if finite.any()
                            else None,
                            ess=ess,
                        )
                    )
    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    out = Path("results")
    out.mkdir(exist_ok=True)
    with (out / "replicates.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = []
    for n in config["calibration_sizes"]:
        for scenario in ("no_shift", "covariate_shift", "conditional_shift"):
            for method in ("unweighted", "naive_weighted", "correct_weighted"):
                group = [
                    r
                    for r in rows
                    if r["n"] == n
                    and r["scenario"] == scenario
                    and r["method"] == method
                ]
                coverage = np.array([r["coverage"] for r in group])
                width = [
                    r["finite_mean_width"]
                    for r in group
                    if r["finite_mean_width"] is not None
                ]
                summary.append(
                    dict(
                        n=n,
                        scenario=scenario,
                        method=method,
                        coverage=float(coverage.mean()),
                        coverage_mc_se=float(
                            coverage.std(ddof=1) / np.sqrt(len(group))
                        ),
                        high_group_coverage=float(
                            np.mean([r["high_group_coverage"] for r in group])
                        ),
                        finite_rate=float(np.mean([r["finite_rate"] for r in group])),
                        finite_mean_width=float(np.mean(width)) if width else None,
                        mean_ess=float(np.mean([r["ess"] for r in group])),
                    )
                )
    result = dict(
        config=config,
        summary=summary,
        execution=dict(
            seconds=elapsed,
            python_peak_bytes=peak,
            process_maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            python=platform.python_version(),
            numpy=np.__version__,
            platform=platform.platform(),
            processor=platform.processor(),
            cpu_count=__import__("os").cpu_count(),
            notes="tracemalloc tracks Python allocations; RSS is whole-process peak, not method-specific",
        ),
    )
    (out / "summary.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    plt.rcParams.update(
        {"axes.spines.top": False, "axes.spines.right": False, "font.size": 10}
    )
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), layout="constrained")
    colors = ["#4477AA", "#EE7733", "#228833"]
    names = ["unweighted", "naive_weighted", "correct_weighted"]
    for method, color in zip(names, colors):
        for ax, scenario in zip(axes, ["covariate_shift", "conditional_shift"]):
            data = [
                r
                for r in summary
                if r["method"] == method and r["scenario"] == scenario
            ]
            ax.errorbar(
                [r["n"] for r in data],
                [r["coverage"] for r in data],
                yerr=[1.96 * r["coverage_mc_se"] for r in data],
                marker="o",
                label=method,
                color=color,
            )
            ax.axhline(
                1 - config["alpha"], color="#555555", linestyle="--", linewidth=0.6
            )
            ax.set(
                xlabel="Calibration observations",
                ylabel="Marginal coverage",
                ylim=(0.35, 1.01),
                title=scenario.replace("_", " "),
            )
    axes[1].legend(fontsize=8)
    fig.savefig(out / "coverage.png", dpi=160)
    plt.close(fig)
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    run()
