"""Synthetic cash-flow sequence risk audit with common stationary marginal shocks."""

import csv
import itertools
import json
import math
import platform
import sys
import time
import tracemalloc
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.breach import first_breach, minimum_buffer

ROOT = Path(__file__).resolve().parents[1]


def save(path, rows):
    with path.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run() -> None:
    cfg = json.loads((ROOT / "benchmarks/config.json").read_text())
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    start = time.perf_counter()
    tracemalloc.start()
    summary = []
    hazards = []
    trials = []
    curves = []
    for name, P in cfg["models"].items():
        result = first_breach(
            cfg["initial_cash"],
            cfg["horizon"],
            cfg["increments"],
            P,
            cfg["initial_regime"],
        )
        buffer = minimum_buffer(
            cfg["horizon"],
            cfg["increments"],
            P,
            cfg["initial_regime"],
            cfg["target"],
            cfg["maximum_buffer"],
        )
        summary.append(
            {
                "model": name,
                "first_breach": result.breach_probability,
                "terminal_negative": result.terminal_negative,
                "recovered_breach": result.breach_probability
                - result.terminal_negative,
                "survival": result.survival,
                "minimum_buffer": buffer,
                "mass_error": result.maximum_mass_error,
            }
        )
        for day, p in enumerate(result.first_breach, 1):
            hazards.append({"model": name, "day": day, "first_breach_mass": p})
        for b in range(cfg["maximum_buffer"] + 1):
            r = first_breach(
                b, cfg["horizon"], cfg["increments"], P, cfg["initial_regime"]
            )
            curves.append(
                {
                    "model": name,
                    "buffer": b,
                    "first_breach": r.breach_probability,
                    "terminal_negative": r.terminal_negative,
                }
            )
        matrix = np.array(P)
        for seed in range(cfg["seeds"]):
            rng = np.random.default_rng(seed)
            states = (rng.random(cfg["draws"]) >= cfg["initial_regime"][0]).astype(int)
            cash = np.full(cfg["draws"], cfg["initial_cash"])
            ever = np.zeros(cfg["draws"], dtype=bool)
            for _ in range(cfg["horizon"]):
                cash += np.array(cfg["increments"])[states]
                ever |= cash < 0
                states = (rng.random(cfg["draws"]) >= matrix[states, 0]).astype(int)
            estimate = float(ever.mean())
            trials.append(
                {
                    "model": name,
                    "seed": seed,
                    "draws": cfg["draws"],
                    "first_breach": estimate,
                    "terminal_negative": float((cash < 0).mean()),
                    "error": estimate - result.breach_probability,
                }
            )
    seconds = time.perf_counter() - start
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    perf = []
    for horizon in cfg["scaling_horizons"]:
        t = time.perf_counter()
        r = first_breach(
            cfg["initial_cash"],
            horizon,
            cfg["increments"],
            cfg["models"]["persistent"],
            cfg["initial_regime"],
        )
        perf.append(
            {
                "horizon": horizon,
                "seconds": time.perf_counter() - t,
                "peak_states": r.peak_states,
                "mass_error": r.maximum_mass_error,
            }
        )
    save(out / "summary.csv", summary)
    save(out / "first_breach.csv", hazards)
    save(out / "trials.csv", trials)
    save(out / "buffer_curve.csv", curves)
    save(out / "performance.csv", perf)
    P = cfg["models"]["persistent"]
    pi = cfg["initial_regime"]
    oracle = 0.0
    for path in itertools.product([0, 1], repeat=6):
        mass = pi[path[0]] * math.prod(P[a][b] for a, b in itertools.pairwise(path))
        cash = 2
        hit = False
        for state in path:
            cash += cfg["increments"][state]
            hit |= cash < 0
        if hit:
            oracle += mass
    error = abs(
        oracle - first_breach(2, 6, cfg["increments"], P, pi).breach_probability
    )
    iid = summary[0]
    persistent = summary[1]
    meta = {
        "config": cfg,
        "seconds": seconds,
        "peak_tracemalloc_bytes": peak,
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "logical_cpus": __import__("os").cpu_count(),
        "exhaustive_oracle_error": error,
        "hypothesis_passed": persistent["first_breach"] - iid["first_breach"] >= 0.10
        and persistent["recovered_breach"] >= 0.02,
        "expected_daily_cash_increment": sum(
            p * x for p, x in zip(pi, cfg["increments"])
        ),
    }
    (out / "metrics.json").write_text(json.dumps(meta, indent=2))
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for i, row in enumerate(summary):
        axes[0].bar(
            i - 0.17,
            row["first_breach"],
            0.32,
            color="#3567A8",
            label="Primera ruptura" if i == 0 else None,
        )
        axes[0].bar(
            i + 0.17,
            row["terminal_negative"],
            0.32,
            color="#C77432",
            label="Caja final<0" if i == 0 else None,
        )
    axes[0].set(
        xticks=[0, 1],
        xticklabels=["IID", "Persistente"],
        ylabel="Probabilidad",
        title="Reserva 6, horizonte 20, mismos marginales",
    )
    axes[0].legend()
    for name, color in [("iid", "#3567A8"), ("persistent", "#C77432")]:
        selected = [r for r in curves if r["model"] == name]
        axes[1].plot(
            [r["buffer"] for r in selected],
            [r["first_breach"] for r in selected],
            label=name,
            color=color,
        )
    axes[1].axhline(
        cfg["target"], linestyle="--", color="black", label="Objetivo sintético 5%"
    )
    axes[1].set(
        xlabel="Reserva (unidades de caja)",
        ylabel="Probabilidad primera ruptura",
        title="Reserva mínima depende de secuencias",
    )
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(out / "audit.png", dpi=150)
    plt.close(fig)
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    run()
