"""Reproduce paired synthetic OPE benchmarks without network dependencies."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
import random
import statistics
import time
import tracemalloc

from src.ope import METHODS, crossfit_reward, estimate, simulate, true_value

HERE = Path(__file__).resolve().parents[1]
RESULTS = HERE / "results"
SEEDS = 40
N = 600
CLIP = 8.0
MIN_ESS = 30.0
REGIMES = {
    "well_overlap": (0.5, 0.5),
    "weak_overlap": (0.04, 0.04),
    "misreported_propensity": (0.04, 0.20),
}


def bootstrap_paired_ci(pairs: list[tuple[float, float]], seed: int = 20261015) -> tuple[float, float]:
    """95% percentile interval for mean squared-error reduction (IPS - DR)."""
    rng = random.Random(seed)
    n = len(pairs)
    draws = []
    for _ in range(2000):
        draws.append(math.fsum(pairs[rng.randrange(n)][0] - pairs[rng.randrange(n)][1] for _ in range(n)) / n)
    draws.sort()
    return draws[49], draws[1949]


def plot_svg(summary: dict) -> None:
    width, height = 920, 430
    names = list(REGIMES)
    colors = {"ips": "#2c5282", "snips": "#805ad5", "dm": "#38a169", "dr": "#d69e2e", "clipped_ips": "#c53030", "clipped_dr": "#319795"}
    max_rmse = max(summary[r][m]["rmse"] for r in names for m in METHODS)
    yscale = 265 / max_rmse
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             '<text x="25" y="30" font-size="19" font-family="sans-serif">OPE RMSE: 40 paired seeds, 600 observations per seed</text>',
             '<text x="25" y="49" font-size="12" font-family="sans-serif">Synthetic binary bandit; lower is better. No deployment claim.</text>',
             '<line x1="55" y1="340" x2="895" y2="340" stroke="black"/>']
    for i, regime in enumerate(names):
        base = 70 + i * 290
        parts.append(f'<text x="{base + 90}" y="365" text-anchor="middle" font-family="sans-serif" font-size="13">{regime.replace("_", " ")}</text>')
        for j, method in enumerate(METHODS):
            value = summary[regime][method]["rmse"]
            bar_h = value * yscale
            x = base + j * 34
            parts.append(f'<rect x="{x}" y="{340-bar_h:.3f}" width="26" height="{bar_h:.3f}" fill="{colors[method]}"/>')
            parts.append(f'<text x="{x+13}" y="{332-bar_h:.3f}" text-anchor="middle" font-family="sans-serif" font-size="10">{value:.3f}</text>')
    for j, method in enumerate(METHODS):
        x = 45 + j * 145
        parts.append(f'<rect x="{x}" y="396" width="12" height="12" fill="{colors[method]}"/>')
        parts.append(f'<text x="{x+17}" y="407" font-size="12" font-family="sans-serif">{method}</text>')
    parts.append('</svg>')
    (RESULTS / "rmse.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")


def run() -> dict:
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    timings: list[dict] = []
    tracemalloc.start()
    t0 = time.perf_counter()
    for regime, (actual, reported) in REGIMES.items():
        for k in range(SEEDS):
            seed = 20261015 + k
            started = time.perf_counter_ns()
            log = simulate(seed, n=N, target_probability=actual, reported_probability=reported)
            preds = crossfit_reward(log)
            for method in METHODS:
                e = estimate(log, method, clip=CLIP, min_ess=MIN_ESS, predictions=preds)
                rows.append({
                    "regime": regime, "seed": seed, "n": N, "method": method,
                    "value": f"{e.value:.12f}", "truth": f"{true_value():.12f}",
                    "error": f"{e.value-true_value():.12f}", "ess": f"{e.ess:.6f}",
                    "matched": e.matched, "warning": e.warning,
                })
            timings.append({"regime": regime, "seed": seed, "elapsed_ms": round((time.perf_counter_ns()-started)/1e6, 5)})
    elapsed = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    with (RESULTS / "raw.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (RESULTS / "timings.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(timings[0]))
        writer.writeheader()
        writer.writerows(timings)
    summary: dict = {}
    for regime in REGIMES:
        summary[regime] = {}
        for method in METHODS:
            selected = [r for r in rows if r["regime"] == regime and r["method"] == method]
            errors = [float(r["error"]) for r in selected]
            summary[regime][method] = {
                "bias": round(statistics.mean(errors), 6),
                "rmse": round(math.sqrt(statistics.mean(x*x for x in errors)), 6),
                "mae": round(statistics.mean(abs(x) for x in errors), 6),
                "abstention_fraction": round(statistics.mean(r["warning"] != "OK" for r in selected), 6),
                "mean_ess": round(statistics.mean(float(r["ess"]) for r in selected), 3),
            }
        ips = {r["seed"]: float(r["error"])**2 for r in rows if r["regime"] == regime and r["method"] == "ips"}
        dr = {r["seed"]: float(r["error"])**2 for r in rows if r["regime"] == regime and r["method"] == "dr"}
        pairs = [(ips[s], dr[s]) for s in sorted(ips)]
        summary[regime]["paired_ips_minus_dr_mse_ci95"] = tuple(round(x, 7) for x in bootstrap_paired_ci(pairs))
    result = {
        "config": {"n_per_seed": N, "seeds": SEEDS, "seed_start": 20261015, "clip": CLIP,
                   "min_ess": MIN_ESS, "regimes": REGIMES, "reward_matrix": [[0.15, 0.55], [0.70, 0.30]],
                   "target": "a=1-x", "folds": 3, "synthetic_truth": true_value(),
                   "hardware": "machine-dependent; see timings.csv; no hardware-normalized speed claim"},
        "runs": len(rows), "summary": summary,
        "performance": {"total_elapsed_seconds": round(elapsed, 6), "peak_tracemalloc_bytes": peak,
                        "caveat": "tracemalloc captures Python allocations, not full process RSS"},
    }
    (RESULTS / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    plot_svg(summary)
    print(f"{len(rows)} estimator results, {SEEDS * len(REGIMES)} paired datasets, truth={true_value():.3f}")
    for regime in REGIMES:
        print(regime, " ".join(f"{m}={summary[regime][m]['rmse']:.4f}" for m in METHODS))
        print("  low_ESS_fraction=", summary[regime]["dr"]["abstention_fraction"],
              "IPS-DR MSE CI=", summary[regime]["paired_ips_minus_dr_mse_ci95"])
    print(f"wall_seconds={elapsed:.3f} peak_tracemalloc_bytes={peak}")
    return result


if __name__ == "__main__":
    run()
