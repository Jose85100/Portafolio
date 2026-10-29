"""Tiny exact-model audit:31buffers, four static corners, no Monte Carlo."""

import csv
import hashlib
import itertools
import json
import math
import platform
import sys
import time
import tracemalloc
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.baseline import PATH, nominal
from src.model import risk_band

ROOT = Path(__file__).resolve().parents[1]


def run() -> None:
    cfg = json.loads((ROOT / "benchmarks/config.json").read_text())
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    start = time.perf_counter()
    tracemalloc.start()
    rows = []
    for cash in range(cfg["buffers"]):
        band = risk_band(cash, cfg["horizon"], cfg["bounds"], cfg["initial"])
        base = nominal(
            cash, cfg["horizon"], cfg["nominal_stress_probabilities"], cfg["initial"]
        )
        corners = [
            nominal(cash, cfg["horizon"], q, cfg["initial"])
            for q in itertools.product(*cfg["bounds"])
        ]
        rows.append(
            {
                "cash": cash,
                "lower": band.lower,
                "nominal": base,
                "upper": band.upper,
                "largest_static_corner": max(corners),
                "adaptive_minus_static_corner": band.upper - max(corners),
                "visited_states": band.visited_states,
            }
        )
    seconds = time.perf_counter() - start
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    with (out / "curves.csv").open("w") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    nominal_buffer = next(
        (r["cash"] for r in rows if r["nominal"] <= cfg["target"]), None
    )
    robust_buffer = next((r["cash"] for r in rows if r["upper"] <= cfg["target"]), None)
    selected = rows[cfg["cash"]]
    meta = {
        "config": cfg,
        "selected": selected,
        "nominal_buffer": nominal_buffer,
        "robust_buffer": robust_buffer,
        "seconds": seconds,
        "peak_tracemalloc_bytes": peak,
        "python": sys.version,
        "platform": platform.platform(),
        "logical_cpus": __import__("os").cpu_count(),
        "baseline_sha256": hashlib.sha256(PATH.read_bytes()).hexdigest(),
        "maximum_adaptive_static_gap": max(
            abs(r["adaptive_minus_static_corner"]) for r in rows
        ),
        "two_day_oracle_error": abs(
            risk_band(0, 2, [[0.1, 0.4], [0.2, 0.8]], [1, 0]).upper - 0.4
        ),
        "hypothesis_passed": selected["upper"] - selected["nominal"] >= 0.05
        and robust_buffer is not None
        and nominal_buffer is not None
        and robust_buffer - nominal_buffer >= 3,
    }
    (out / "metrics.json").write_text(json.dumps(meta, indent=2))
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    xs = [r["cash"] for r in rows]
    axes[0].fill_between(
        xs,
        [r["lower"] for r in rows],
        [r["upper"] for r in rows],
        color="#3567A8",
        alpha=0.2,
        label="Banda rectangular",
    )
    axes[0].plot(
        xs, [r["nominal"] for r in rows], color="#3567A8", label="Matriz nominal"
    )
    axes[0].plot(xs, [r["upper"] for r in rows], color="#C77432", label="Cota robusta")
    axes[0].axhline(
        cfg["target"], color="black", linestyle="--", label="Objetivo sintético 5%"
    )
    axes[0].set(
        xlabel="Reserva (unidades de caja)",
        ylabel="Probabilidad primera ruptura",
        title="Ambigüedad de transición cambia reserva",
    )
    axes[0].legend(fontsize=8)
    axes[1].bar(
        ["Nominal", "Robusta"],
        [v if v is not None else math.nan for v in [nominal_buffer, robust_buffer]],
        color=["#3567A8", "#C77432"],
    )
    axes[1].set(
        ylabel="Reserva mínima en rejilla", title="Horizonte 20; intervalos hipotéticos"
    )
    fig.tight_layout()
    fig.savefig(out / "audit.png", dpi=150)
    plt.close(fig)
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    run()
