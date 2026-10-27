"""Deterministic comparative statics, solver audit and implementation stress."""

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
import scipy
from src.screening import (
    Economy,
    analytic,
    uniform,
    profit,
    slacks,
    strictify,
    qp,
    realized,
)

ROOT = Path(__file__).resolve().parents[1]


def run() -> None:
    cfg = json.loads((ROOT / "config.json").read_text())
    rows = []
    start = time.perf_counter()
    tracemalloc.start()
    for low, high in cfg["type_pairs"]:
        for cost in cfg["costs"]:
            for p in cfg["probabilities"]:
                e = Economy(low, high, p, cost)
                menu = analytic(e)
                num, iterations = qp(e)
                kind, base, bp = uniform(e)
                rows.append(
                    {
                        "low": low,
                        "high": high,
                        "p": p,
                        "cost": cost,
                        "qL": menu[0],
                        "qH": menu[1],
                        "tL": menu[2],
                        "tH": menu[3],
                        "menu_profit": profit(menu, e),
                        "baseline": kind,
                        "baseline_profit": bp,
                        "qp_profit": profit(num, e),
                        "profit_gap": abs(profit(num, e) - profit(menu, e)),
                        "minimum_slack": slacks(menu, e).min(),
                        "quantity_error": float(np.max(np.abs(num[:2] - menu[:2]))),
                        "iterations": iterations,
                    }
                )
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    e = Economy(**cfg["anchor"])
    a = analytic(e)
    s = strictify(a, e, cfg["epsilon"])
    kind, b, bp = uniform(e)
    anchor = {
        "weak_menu": a.tolist(),
        "strict_menu": s.tolist(),
        "weak_profit_truthful": profit(a, e),
        "strict_profit": profit(s, e),
        "uniform_type": kind,
        "uniform_profit": bp,
        "uniform_strict_profit": bp - cfg["epsilon"]
        if kind == "pooling"
        else bp - e.p * cfg["epsilon"],
        "weak_adverse_tie_profit": realized(a, e, tie="smallest"),
        "strict_adverse_tie_profit": realized(s, e, tie="smallest"),
        "misspecified_low_profit": realized(s, e, true_low=cfg["stress_true_low"]),
        "informed_true_uniform_profit": uniform(
            Economy(cfg["stress_true_low"], e.high, e.p, e.cost)
        )[2],
        "first_best_observable_type_profit": (1 - e.p) * e.low**2 / (2 * e.cost)
        + e.p * e.high**2 / (2 * e.cost),
        "strict_slacks": slacks(s, e).tolist(),
    }
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    with (out / "grid.csv").open("w") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    data = {
        "config": cfg,
        "anchor": anchor,
        "grid_count": len(rows),
        "max_qp_profit_gap": max(r["profit_gap"] for r in rows),
        "max_quantity_error": max(r["quantity_error"] for r in rows),
        "minimum_slack": min(r["minimum_slack"] for r in rows),
        "seconds": time.perf_counter() - start,
        "python_peak_bytes": peak,
        "hardware": platform.platform(),
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "data_sha256": hashlib.sha256((out / "grid.csv").read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(
            (ROOT / "src/screening.py").read_bytes()
        ).hexdigest(),
        "timing_note": "Whole grid analytic/QP instrumented; peak Python allocations, not RSS. Deterministic calibration: no sampling confidence intervals.",
    }
    (out / "summary.json").write_text(json.dumps(data, indent=2))
    selected = [r for r in rows if r["low"] == 1 and r["high"] == 2 and r["cost"] == 1]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout="constrained")
    ps = [r["p"] for r in selected]
    axes[0].plot(
        ps,
        [r["menu_profit"] for r in selected],
        "-o",
        color="#0072B2",
        label="IC/IR menu",
    )
    axes[0].plot(
        ps,
        [r["baseline_profit"] for r in selected],
        "--s",
        color="#D55E00",
        label="Best uniform contract",
    )
    axes[0].set_xlabel("Probability of high type p")
    axes[0].set_ylabel("Expected principal profit (normalized units)")
    axes[0].legend()
    axes[1].bar(
        [
            "Weak menu\nadverse ties",
            "Strict menu\nadverse ties",
            "Strict menu\nwrong low type",
        ],
        [
            anchor["weak_adverse_tie_profit"],
            anchor["strict_adverse_tie_profit"],
            anchor["misspecified_low_profit"],
        ],
        color=["#D55E00", "#0072B2", "#009E73"],
    )
    axes[1].axhline(bp, color="black", ls="--", label="Anchor best uniform")
    axes[1].set_ylabel("Realized expected profit | p=0.2")
    axes[1].legend()
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.2)
    fig.suptitle(
        "Static screening: incentives, implementation and misspecification | synthetic"
    )
    fig.savefig(out / "comparison.png", dpi=150)
    plt.close(fig)
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    run()
