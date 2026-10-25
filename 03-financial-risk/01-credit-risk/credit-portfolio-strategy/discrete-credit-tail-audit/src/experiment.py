"""Synthetic concentration audit; exact refers to lattice model, not empirical truth."""

import csv
import itertools
import json
import platform
import sys
import time
import tracemalloc
from fractions import Fraction
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.loss import independent_pmf, normal_tail, tail

ROOT = Path(__file__).resolve().parents[1]


def csv_write(path, rows):
    with path.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run() -> None:
    cfg = json.loads((ROOT / "benchmarks/config.json").read_text())
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    cfg["cases"]["granular"] = [3] * cfg["granular_count"]
    summary = []
    trials = []
    mass_rows = []
    start = time.perf_counter()
    tracemalloc.start()
    for name, weights in cfg["cases"].items():
        ps = [cfg["pd"]] * len(weights)
        pmf = independent_pmf(weights, ps)
        exact = tail(pmf, cfg["confidence"])
        normal = normal_tail(weights, ps, cfg["confidence"])
        summary.append(
            {
                "case": name,
                "n": len(weights),
                "total_loss": sum(weights),
                "hhi": sum(w * w for w in weights) / sum(weights) ** 2,
                "dp_var": exact.var,
                "dp_es": exact.es,
                "normal_var": normal.var,
                "normal_es": normal.es,
                "normal_es_relative_error": (normal.es - exact.es) / exact.es,
                "mass_error": abs(sum(pmf) - 1),
            }
        )
        for value, mass in enumerate(pmf):
            mass_rows.append({"case": name, "loss": value, "probability": mass})
        for seed in range(cfg["mc_seeds"]):
            rng = np.random.default_rng(seed)
            losses = (
                rng.random((cfg["mc_draws"], len(weights))) < np.array(ps)
            ) @ np.array(weights)
            counts = np.bincount(losses, minlength=sum(weights) + 1) / cfg["mc_draws"]
            estimate = tail(counts.tolist(), cfg["confidence"])
            trials.append(
                {
                    "case": name,
                    "seed": seed,
                    "draws": cfg["mc_draws"],
                    "var": estimate.var,
                    "es": estimate.es,
                    "es_error": estimate.es - exact.es,
                }
            )
    seconds = time.perf_counter() - start
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    csv_write(out / "summary.csv", summary)
    csv_write(out / "trials.csv", trials)
    csv_write(out / "pmf.csv", mass_rows)
    perf = []
    for n in [20, 100, 300]:
        t = time.perf_counter()
        pmf = independent_pmf([3] * n, [0.02] * n)
        elapsed = time.perf_counter() - t
        perf.append(
            {
                "n": n,
                "lattice": len(pmf),
                "seconds": elapsed,
                "mass_error": abs(sum(pmf) - 1),
            }
        )
    csv_write(out / "performance.csv", perf)
    # Falsification: same mean, perfectly dependent defaults instead of independence.
    dependent_pmf = [0.0] * 301
    dependent_pmf[0] = 0.98
    dependent_pmf[300] = 0.02
    common_shock = tail(dependent_pmf, cfg["confidence"])
    concentrated = next(r for r in summary if r["case"] == "concentrated")
    oracle_weights = [1, 3, 7]
    oracle_probabilities = [Fraction(".02"), Fraction(".1"), Fraction(".3")]
    oracle = [Fraction(0)] * (sum(oracle_weights) + 1)
    for bits in itertools.product([0, 1], repeat=3):
        probability = __import__("math").prod(
            p if b else 1 - p for p, b in zip(oracle_probabilities, bits)
        )
        oracle[sum(w * b for w, b in zip(oracle_weights, bits))] += probability
    dp_small = independent_pmf(oracle_weights, [float(p) for p in oracle_probabilities])
    max_oracle_error = max(
        abs(actual - float(expected)) for actual, expected in zip(dp_small, oracle)
    )
    meta = {
        "max_oracle_pmf_error": max_oracle_error,
        "oracle_tolerance_passed": max_oracle_error <= 1e-12,
        "config": cfg,
        "seconds": seconds,
        "peak_tracemalloc_bytes": peak,
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "logical_cpus": __import__("os").cpu_count(),
        "hypothesis_concentration_passed": concentrated["normal_es_relative_error"]
        < -0.3,
        "negative_common_shock_var": common_shock.var,
        "negative_common_shock_es": common_shock.es,
    }
    (out / "metrics.json").write_text(json.dumps(meta, indent=2))
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for i, row in enumerate(summary):
        axes[0].bar(
            i - 0.17,
            row["dp_es"],
            0.32,
            color="#3567A8",
            label="DP" if i == 0 else None,
        )
        axes[0].bar(
            i + 0.17,
            row["normal_es"],
            0.32,
            color="#C77432",
            label="Normal" if i == 0 else None,
        )
    axes[0].set(
        xticks=[0, 1],
        xticklabels=["Granular", "Concentrada"],
        ylabel="ES99 (unidades de pérdida)",
        title="Misma pérdida total y PD; distinta concentración",
    )
    axes[0].legend()
    axes[1].boxplot(
        [[r["es_error"] for r in trials if r["case"] == name] for name in cfg["cases"]],
        tick_labels=["Granular", "Concentrada"],
    )
    axes[1].axhline(0, color="black", linestyle="--")
    axes[1].set(
        title="Monte Carlo:30 semillas,10.000 draws",
        ylabel="Error ES99 vs DP (unidades)",
    )
    fig.tight_layout()
    fig.savefig(out / "audit.png", dpi=150)
    plt.close(fig)
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    run()
