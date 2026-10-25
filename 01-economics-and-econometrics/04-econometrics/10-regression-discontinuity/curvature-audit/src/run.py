"""Paired bandwidth audit with raw estimates and Monte Carlo uncertainty."""

from __future__ import annotations
import csv
import hashlib
import json
import platform
import time
import tracemalloc
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from src.rd import estimate, sample

ROOT = Path(__file__).resolve().parents[1]


def run() -> None:
    cfg = json.loads((ROOT / "config.json").read_text())
    rows = []
    summary = []
    costs = []
    for scenario in cfg["scenarios"]:
        start = time.perf_counter()
        tracemalloc.start()
        draws = []
        for rep in range(cfg["replications"]):
            seed = cfg["seed"] + rep
            x, y = sample(
                seed,
                cfg["n"],
                scenario["curvature"],
                scenario["latent_jump"],
                cfg["noise_sd"],
            )
            values = []
            for h in cfg["bandwidths"]:
                value, nl, nr = estimate(x, y, h)
                values.append(value)
                rows.append(
                    {
                        "scenario": scenario["name"],
                        "seed": seed,
                        "h": h,
                        "estimate": value,
                        "n_left": nl,
                        "n_right": nr,
                        "true_effect": cfg["truth"],
                    }
                )
            draws.append(values)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        costs.append(
            {
                "scenario": scenario["name"],
                "seconds": time.perf_counter() - start,
                "python_peak_bytes": peak,
            }
        )
        a = np.array(draws)
        errors = a - cfg["truth"]
        sq = errors**2
        for i, h in enumerate(cfg["bandwidths"]):
            diff = sq[:, i] - sq[:, 0]
            summary.append(
                {
                    "scenario": scenario["name"],
                    "h": h,
                    "mean": float(a[:, i].mean()),
                    "bias": float(errors[:, i].mean()),
                    "sd": float(a[:, i].std(ddof=1)),
                    "rmse": float(np.sqrt(sq[:, i].mean())),
                    "mean_mc_se": float(a[:, i].std(ddof=1) / np.sqrt(len(a))),
                    "paired_mse_difference": float(diff.mean()),
                    "paired_mse_se": float(diff.std(ddof=1) / np.sqrt(len(a))),
                    "q025": float(np.quantile(a[:, i], 0.025)),
                    "q975": float(np.quantile(a[:, i], 0.975)),
                }
            )
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    with (out / "replications.csv").open("w") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    payload = {
        "config": cfg,
        "summary": summary,
        "costs": costs,
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "hardware": platform.platform(),
        "cpu": platform.processor() or platform.machine(),
        "source_sha256": hashlib.sha256((ROOT / "src/rd.py").read_bytes()).hexdigest(),
        "data_sha256": hashlib.sha256(
            (out / "replications.csv").read_bytes()
        ).hexdigest(),
        "timing_note": "Combined simulation/all bandwidths; tracemalloc Python allocation peak, not RSS.",
    }
    (out / "summary.json").write_text(json.dumps(payload, indent=2))
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.7), layout="constrained")
    for scenario, color in zip(cfg["scenarios"], ["#0072B2", "#D55E00", "#009E73"]):
        ss = [s for s in summary if s["scenario"] == scenario["name"]]
        hs = [s["h"] for s in ss]
        axes[0].errorbar(
            hs,
            [s["mean"] for s in ss],
            yerr=[1.96 * s["mean_mc_se"] for s in ss],
            marker="o",
            color=color,
            label=scenario["name"],
        )
        axes[1].plot(
            hs, [s["rmse"] for s in ss], marker="o", color=color, label=scenario["name"]
        )
    axes[0].axhline(1, color="black", ls="--", label="True causal effect=1")
    axes[0].set_ylabel("Mean discontinuity estimate ±1.96 MC SE")
    axes[1].set_ylabel("RMSE relative to true effect=1")
    for ax in axes:
        ax.set_xlabel("Bandwidth h (running-variable units)")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=0.2)
    axes[0].legend(fontsize=8)
    fig.suptitle(
        "Sharp RD: curvature, bandwidth and continuity violation | synthetic n=1200"
    )
    fig.savefig(out / "comparison.png", dpi=150)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
