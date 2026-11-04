"""Synthetic reproducibility/accuracy comparison of merge trees."""

import csv
import json
import random
import time
import math
from decimal import Decimal, localcontext
from statistics import median
from pathlib import Path
import matplotlib.pyplot as plt
from src.dynamic import DynamicMoments
from src.reduction import merge_balanced

ROOT = Path(__file__).resolve().parents[1]


def summarize(xs):
    state = DynamicMoments()
    for x in xs:
        state = state.push(x)
    return state


def run():
    rows = []
    for seed in (1104, 1105, 1106):
        rng = random.Random(seed)
        for n in (256, 4096):
            xs = [1e8 + rng.gauss(0, 0.01) for _ in range(n)]
            chunks = [summarize(xs[i : i + 32]) for i in range(0, n, 32)]
            with localcontext() as ctx:
                ctx.prec = 100
                dec = [Decimal.from_float(x) for x in xs]
                mean = sum(dec) / len(dec)
                oracle = float((sum((x - mean) ** 2 for x in dec) / len(dec)).sqrt())
            methods = {
                "left": lambda: _fold(chunks),
                "reverse": lambda: _fold(chunks[::-1]),
                "balanced": lambda: merge_balanced(chunks),
            }
            outputs = {}
            for name, method in methods.items():
                start = time.perf_counter_ns()
                state = method()
                elapsed = time.perf_counter_ns() - start
                outputs[name] = state.result().std
                rows.append(
                    {
                        "seed": seed,
                        "n": n,
                        "method": name,
                        "std": outputs[name],
                        "oracle_std": oracle,
                        "abs_error": abs(outputs[name] - oracle),
                        "tolerance": max(4 * math.ulp(oracle), 1e-12 * oracle),
                        "within_tolerance": abs(outputs[name] - oracle)
                        <= max(4 * math.ulp(oracle), 1e-12 * oracle),
                        "elapsed_ns": elapsed,
                    }
                )
            for row in rows[-3:]:
                row["spread_vs_tree_min"] = max(outputs.values()) - min(
                    outputs.values()
                )
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    with (out / "reduction_raw.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    errors = [r["abs_error"] for r in rows]
    summary = {
        "seeds": [1104, 1105, 1106],
        "sizes": [256, 4096],
        "chunk_size": 32,
        "methods": ["left", "reverse", "balanced"],
        "rows": len(rows),
        "max_tree_spread_sd": max(r["spread_vs_tree_min"] for r in rows),
        "oracle_error_abs_min": min(errors),
        "oracle_error_abs_median": median(errors),
        "oracle_error_abs_max": max(errors),
        "all_within_declared_tolerance": all(r["within_tolerance"] for r in rows),
        "data": "synthetic Gaussian around 1e8; known scale 0.01; not empirical",
    }
    (out / "reduction_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    fig, ax = plt.subplots(figsize=(7, 4))
    for method in ("left", "reverse", "balanced"):
        vals = [
            r["abs_error"] for r in rows if r["n"] == 4096 and r["method"] == method
        ]
        ax.plot([1, 2, 3], vals, marker="o", label=method)
    ax.set(
        title="Chan merge order: SD error vs Decimal oracle",
        xlabel="Seed index",
        ylabel="Absolute SD error (value units)",
    )
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "reduction_order.png", dpi=150)
    print(json.dumps(summary, sort_keys=True))
    return summary


def _fold(chunks):
    state = DynamicMoments()
    for chunk in chunks:
        state = state.merge(chunk)
    return state


if __name__ == "__main__":
    run()
