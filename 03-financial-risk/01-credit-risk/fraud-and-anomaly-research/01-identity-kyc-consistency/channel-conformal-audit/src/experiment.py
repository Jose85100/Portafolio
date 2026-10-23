"""Synthetic audit: no customer data, no operational fraud claims."""

import csv
import json
import platform
import resource
import sys
import time
from pathlib import Path
import tracemalloc
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.conformal import TailCalibrator

ROOT = Path(__file__).resolve().parents[1]


def run() -> dict:
    config = json.loads((ROOT / "benchmarks/config.json").read_text())
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    rows = []
    tracemalloc.start()
    start = time.perf_counter()
    for scenario in ("stationary", "drift", "sparse"):
        n = (
            config["sparse_calibration_per_channel"]
            if scenario == "sparse"
            else config["calibration_per_channel"]
        )
        for seed in range(config["seeds"]):
            rng = np.random.default_rng(seed)
            cal = [
                np.round(np.abs(rng.normal(0, scale, n)), 1).tolist()
                for scale in config["channel_scales"]
            ]
            pooled = TailCalibrator(cal[0] + cal[1])
            for channel, scale in enumerate(config["channel_scales"]):
                calibrator = TailCalibrator(cal[channel])
                multiplier = config["drift_multiplier"] if scenario == "drift" else 1
                normal = np.round(
                    np.abs(
                        rng.normal(
                            0, scale * multiplier, config["test_inliers_per_channel"]
                        )
                    ),
                    1,
                )
                anomaly = np.round(
                    np.abs(
                        rng.normal(
                            config["anomaly_shift_sigma"] * scale,
                            scale,
                            config["test_outliers_per_channel"],
                        )
                    ),
                    1,
                )
                for method, model in (("pooled", pooled), ("channel", calibrator)):
                    for kind, scores in (("inlier", normal), ("outlier", anomaly)):
                        count = sum(
                            model.alert(float(x), config["alpha"]) for x in scores
                        )
                        rows.append(
                            dict(
                                scenario=scenario,
                                seed=seed,
                                channel=channel,
                                method=method,
                                kind=kind,
                                alerts=count,
                                n=len(scores),
                                rate=count / len(scores),
                            )
                        )
    duration = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    with (output / "trials.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = []
    for scenario in ("stationary", "drift", "sparse"):
        for method in ("pooled", "channel"):
            for channel in (0, 1):
                for kind in ("inlier", "outlier"):
                    subset = [
                        r
                        for r in rows
                        if (r["scenario"], r["method"], r["channel"], r["kind"])
                        == (scenario, method, channel, kind)
                    ]
                    rates = np.array([r["rate"] for r in subset])
                    summary.append(
                        dict(
                            scenario=scenario,
                            method=method,
                            channel=channel,
                            kind=kind,
                            mean_rate=float(rates.mean()),
                            seed_standard_error=float(
                                rates.std(ddof=1) / np.sqrt(len(rates))
                            ),
                        )
                    )
    with (output / "summary.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    def rate(scenario, method, channel, kind):
        return next(
            r["mean_rate"]
            for r in summary
            if (r["scenario"], r["method"], r["channel"], r["kind"])
            == (scenario, method, channel, kind)
        )

    gaps = {
        method: abs(
            rate("stationary", method, 1, "inlier")
            - rate("stationary", method, 0, "inlier")
        )
        for method in ("pooled", "channel")
    }
    metrics = {
        "fpr_gap": gaps,
        "gap_reduction": gaps["pooled"] - gaps["channel"],
        "hypothesis_passed": gaps["pooled"] - gaps["channel"] >= 0.03,
        "elapsed_seconds": duration,
        "peak_tracemalloc_bytes": peak,
        "max_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "matplotlib": matplotlib.__version__,
        "config": config,
    }
    (output / "metrics.json").write_text(json.dumps(metrics, indent=2))
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.7), sharey=True)
    colors = ("#3567A8", "#C77432")
    for ax, scenario in zip(axes, ("stationary", "drift", "sparse")):
        for offset, method, color in zip((-0.18, 0.18), ("pooled", "channel"), colors):
            means = [rate(scenario, method, g, "inlier") for g in (0, 1)]
            ax.bar(np.array([0, 1]) + offset, means, 0.34, label=method, color=color)
        ax.axhline(config["alpha"], color="black", linestyle="--", label="alpha 5%")
        ax.set(
            title=scenario,
            xticks=[0, 1],
            xticklabels=["Canal sigma=1", "Canal sigma=4"],
            ylim=(0, 0.38),
        )
    axes[0].set_ylabel("Fracción de inliers alertados")
    axes[-1].legend(fontsize=8)
    fig.suptitle("Alertas KYC sintéticas: calibración por canal y límites")
    fig.tight_layout()
    fig.savefig(output / "audit.png", dpi=160)
    plt.close(fig)
    print(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    run()
