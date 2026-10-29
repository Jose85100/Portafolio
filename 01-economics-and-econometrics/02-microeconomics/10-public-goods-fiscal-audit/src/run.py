"""Small deterministic audit; no long simulation or sampled confidence claims."""

from __future__ import annotations
import csv
import hashlib
import json
import platform
import time
import tracemalloc
from pathlib import Path
from typing import Any
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from src.public_good import optimal, naive, no_policy, policy_welfare, oracle

ROOT = Path(__file__).resolve().parents[1]


def run() -> None:
    cfg = json.loads((ROOT / "config.json").read_text())
    rows: list[dict[str, Any]] = []
    tracemalloc.start()
    start = time.perf_counter()
    for low in cfg["low_values"]:
        for high in cfg["high_values"]:
            for tax in cfg["tax_cost_values"]:
                began = time.perf_counter()
                g = optimal(low, high, tax)
                analytic_seconds = time.perf_counter() - began
                w, s, budget = policy_welfare(g, low, high, tax)
                began = time.perf_counter()
                g_num, w_num = oracle(low, high, tax)
                oracle_seconds = time.perf_counter() - began
                base = policy_welfare(no_policy(high), low, high, tax)[0]
                ignorant = policy_welfare(naive(low, high), low, high, tax)[0]
                rows.append(
                    {
                        "low": low,
                        "high": high,
                        "tax_cost": tax,
                        "G_no_policy": no_policy(high),
                        "G_naive": naive(low, high),
                        "G_aware": g,
                        "welfare_no_policy": base,
                        "welfare_naive": ignorant,
                        "welfare_aware": w,
                        "matching_share": s,
                        "public_budget": budget,
                        "G_oracle": g_num,
                        "oracle_welfare_gap": abs(w - w_num),
                        "analytic_seconds": analytic_seconds,
                        "oracle_seconds": oracle_seconds,
                    }
                )
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed = time.perf_counter() - start
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    with (out / "cases.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    anchor = next(
        r
        for r in rows
        if r["low"] == cfg["anchor"]["low"]
        and r["high"] == cfg["anchor"]["high"]
        and r["tax_cost"] == cfg["anchor"]["tax_cost"]
    )
    costs = [
        {
            "prefix_cases": n,
            "analytic_seconds": sum(r["analytic_seconds"] for r in rows[:n]),
            "oracle_seconds": sum(r["oracle_seconds"] for r in rows[:n]),
        }
        for n in [1, 10, 30]
    ]
    with (out / "costs.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(costs[0]))
        writer.writeheader()
        writer.writerows(costs)
    payload = {
        "config": cfg,
        "case_count": len(rows),
        "anchor": anchor,
        "max_oracle_welfare_gap": max(r["oracle_welfare_gap"] for r in rows),
        "min_gain_vs_no_policy": min(
            r["welfare_aware"] - r["welfare_no_policy"] for r in rows
        ),
        "min_gain_vs_naive": min(r["welfare_aware"] - r["welfare_naive"] for r in rows),
        "seconds": elapsed,
        "python_peak_bytes": peak,
        "hardware": platform.platform(),
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "source_sha256": hashlib.sha256(
            (ROOT / "src/public_good.py").read_bytes()
        ).hexdigest(),
        "data_sha256": hashlib.sha256((out / "cases.csv").read_bytes()).hexdigest(),
        "timing_note": "Per-arm scalar times measured once, prefix totals are batch aggregation not repeated runs; peak is whole experiment Python allocations, not RSS. No tax estimation or operational benchmark.",
    }
    (out / "summary.json").write_text(json.dumps(payload, indent=2))
    selected = [r for r in rows if r["low"] == 1 and r["high"] == 2]
    taxes = [r["tax_cost"] for r in selected]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.3), layout="constrained")
    for key, label, color in [
        ("welfare_no_policy", "No policy", "#333333"),
        ("welfare_naive", "Ignore fiscal cost", "#D55E00"),
        ("welfare_aware", "Account for fiscal cost", "#0072B2"),
    ]:
        axes[0].plot(taxes, [r[key] for r in selected], "-o", label=label, color=color)
    axes[0].set_ylabel("Net social welfare (normalized units)")
    axes[0].legend(fontsize=8)
    axes[1].plot(
        taxes,
        [r["matching_share"] for r in selected],
        "-o",
        color="#0072B2",
        label="Budget-aware share",
    )
    axes[1].axhline(1 / 3, color="#D55E00", ls="--", label="Zero-distortion share")
    axes[1].set_ylabel("Matching subsidy share s")
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.set_xlabel("Additional fiscal resource cost lambda")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=0.2)
    fig.suptitle("Public good: financing is not free | synthetic two-agent model")
    fig.savefig(out / "comparison.png", dpi=150)
    plt.close(fig)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    run()
