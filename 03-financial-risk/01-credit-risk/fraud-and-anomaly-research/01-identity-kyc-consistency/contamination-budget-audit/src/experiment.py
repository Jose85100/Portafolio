"""Synthetic contamination audit, common random numbers across policies."""

import csv
import json
import platform
import sys
import time
import tracemalloc
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.guard import ContaminationGuard

ROOT = Path(__file__).resolve().parents[1]


def run() -> None:
    cfg = json.loads((ROOT / "benchmarks/config.json").read_text())
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    rows = []
    start = time.perf_counter()
    tracemalloc.start()
    for seed in range(cfg["seeds"]):
        rng = np.random.default_rng(seed)
        n = cfg["calibration_size"]
        m = int(n * cfg["contamination_fraction"])
        normal = np.abs(rng.normal(size=cfg["test_inliers"]))
        anomaly = np.abs(rng.normal(cfg["anomaly_shift"], 1, cfg["test_outliers"]))
        calibration = np.abs(rng.normal(size=n))
        for scenario in cfg["scenarios"]:
            actual = 0 if scenario == "clean" else m
            scores = np.concatenate(
                (
                    calibration[: n - actual],
                    np.full(
                        actual, 100.0 if scenario == "high-score-contamination" else 0.0
                    ),
                )
            )
            bound = int(m / 2) if scenario == "understated-bound" else m
            # In clean scenario use conservative upper bound m despite no contamination.
            for method, cap in [("ordinary", 0), ("guard", bound)]:
                model = ContaminationGuard(scores.tolist(), cap)
                for kind, test in [("inlier", normal), ("outlier", anomaly)]:
                    alerts = sum(model.alert(float(s), cfg["alpha"]) for s in test)
                    rows.append(
                        {
                            "seed": seed,
                            "scenario": scenario,
                            "method": method,
                            "kind": kind,
                            "actual_contaminants": actual,
                            "bound": cap,
                            "alerts": alerts,
                            "n": len(test),
                            "rate": alerts / len(test),
                        }
                    )
    elapsed = time.perf_counter() - start
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    with (out / "trials.csv").open("w") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    summary = []
    for scenario in cfg["scenarios"]:
        for method in ["ordinary", "guard"]:
            for kind in ["inlier", "outlier"]:
                rates = np.array(
                    [
                        r["rate"]
                        for r in rows
                        if (r["scenario"], r["method"], r["kind"])
                        == (scenario, method, kind)
                    ]
                )
                summary.append(
                    {
                        "scenario": scenario,
                        "method": method,
                        "kind": kind,
                        "mean": float(rates.mean()),
                        "se_seeds": float(rates.std(ddof=1) / np.sqrt(len(rates))),
                    }
                )
    with (out / "summary.csv").open("w") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)

    def val(s, m, k):
        return next(
            r["mean"]
            for r in summary
            if (r["scenario"], r["method"], r["kind"]) == (s, m, k)
        )

    hypothesis = (
        val("low-score-contamination", "guard", "inlier") <= 0.055
        and val("low-score-contamination", "ordinary", "inlier")
        - val("low-score-contamination", "guard", "inlier")
        >= 0.02
    )
    perf = []
    for size in [100, 1000, 10000]:
        values = np.arange(size).tolist()
        t = time.perf_counter()
        model = ContaminationGuard(values, size // 5)
        fit = time.perf_counter() - t
        t = time.perf_counter()
        for i in range(10000):
            model.p_value(float(i % size))
        perf.append(
            {
                "n": size,
                "fit_seconds": fit,
                "queries": 10000,
                "query_seconds": time.perf_counter() - t,
            }
        )
    with (out / "performance.csv").open("w") as f:
        w = csv.DictWriter(f, fieldnames=list(perf[0]))
        w.writeheader()
        w.writerows(perf)
    meta = {
        "config": cfg,
        "hypothesis_passed": hypothesis,
        "seconds": elapsed,
        "tracemalloc_peak_bytes": peak,
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "matplotlib": matplotlib.__version__,
        "processor": platform.processor(),
        "logical_cpus": __import__("os").cpu_count(),
    }
    (out / "metrics.json").write_text(json.dumps(meta, indent=2))
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    x = np.arange(4)
    for ax, kind, title in zip(
        axes,
        ["inlier", "outlier"],
        ["Falsas alertas", "Detección de anomalías sintéticas"],
    ):
        for method, offset, color in [
            ("ordinary", -0.17, "#3567A8"),
            ("guard", 0.17, "#C77432"),
        ]:
            selected = [
                next(
                    r
                    for r in summary
                    if (r["scenario"], r["method"], r["kind"]) == (s, method, kind)
                )
                for s in cfg["scenarios"]
            ]
            ax.bar(
                x + offset,
                [r["mean"] for r in selected],
                0.32,
                yerr=[1.96 * r["se_seeds"] for r in selected],
                capsize=3,
                label=method,
                color=color,
            )
        ax.set(
            xticks=x,
            xticklabels=["Limpia", "40% bajos", "Cota errónea", "40% altos"],
            title=title,
            ylabel="Fracción",
        )
        ax.tick_params(axis="x", rotation=20)
    axes[0].axhline(cfg["alpha"], linestyle="--", color="black", label="alpha 5%")
    axes[0].legend()
    fig.suptitle(
        "Referencia KYC contaminada: robustez cuesta potencia; cota debe cumplirse"
    )
    fig.tight_layout()
    fig.savefig(out / "audit.png", dpi=150)
    plt.close(fig)
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    run()
