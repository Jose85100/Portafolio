"""Reproducible paired synthetic study, raw results, bootstrap and SVG figure."""
from __future__ import annotations

import csv
import json
import os
import platform
import random
import statistics
import sys
import time
import tracemalloc
from collections import defaultdict
from pathlib import Path

from src.consensus import POLICIES, REGIMES, decide, evaluate, fit_reliabilities, generate_cases

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
SEEDS = tuple(range(20261022, 20261062))
N_CALIBRATION = 800
N_TEST = 600


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("cannot write empty table")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def bootstrap_mean_ci(values: list[float], seed: int = 932, n: int = 2000) -> tuple[float, float]:
    rng = random.Random(seed)
    samples = [statistics.mean(rng.choices(values, k=len(values))) for _ in range(n)]
    samples.sort()
    return samples[int(n * 0.025)], samples[int(n * 0.975)]


def svg_chart(summary: dict) -> str:
    # Pure SVG; no plotting dependency or network required.
    colors = {"majority": "#64748b", "weighted": "#0f766e", "group_capped": "#2563eb", "wrong_metadata": "#d97706"}
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="510" viewBox="0 0 1040 510">',
           '<rect width="1040" height="510" fill="#f8fafc"/>',
           '<text x="42" y="42" font-family="sans-serif" font-size="23" font-weight="bold" fill="#0f172a">Selective error at 80% coverage</text>',
           '<text x="42" y="66" font-family="sans-serif" font-size="13" fill="#475569">40 paired seeds · synthetic binary agent votes · lower is better</text>']
    for j, (regime, policies) in enumerate(summary.items()):
        left = 55 + j * 330
        out.append(f'<text x="{left}" y="106" font-family="sans-serif" font-size="17" fill="#0f172a">{regime.replace("_", " ")}</text>')
        for k, policy in enumerate(POLICIES):
            value = policies[policy]["risk_at_80"]
            y = 135 + 82 * k
            width = 210 * min(1.0, value / 0.45)
            out.append(f'<text x="{left}" y="{y}" font-family="sans-serif" font-size="13" fill="#334155">{policy.replace("_", " ")}</text>')
            out.append(f'<rect x="{left}" y="{y+10}" width="210" height="17" rx="3" fill="#e2e8f0"/>')
            out.append(f'<rect x="{left}" y="{y+10}" width="{width:.1f}" height="17" rx="3" fill="{colors[policy]}"/>')
            out.append(f'<text x="{left+220}" y="{y+24}" font-family="sans-serif" font-size="12" fill="#0f172a">{value:.3f}</text>')
    out.append('<text x="42" y="492" font-family="sans-serif" font-size="12" fill="#475569">Group labels are assumed known; the experiment does not use real LLMs or validate operational correctness.</text></svg>')
    return "\n".join(out)


def run() -> dict:
    OUT.mkdir(exist_ok=True)
    raw = []
    started = time.perf_counter()
    for regime, p_shared in REGIMES.items():
        for seed in SEEDS:
            calibration = generate_cases(seed, N_CALIBRATION, p_shared)
            test = generate_cases(seed + 1000000, N_TEST, p_shared)
            weights = fit_reliabilities(calibration)
            for policy in POLICIES:
                t0 = time.perf_counter_ns()
                metrics = evaluate(test, weights, policy)
                elapsed_ms = (time.perf_counter_ns() - t0) / 1e6
                raw.append({"regime": regime, "seed": seed, "policy": policy, **metrics, "decision_ms_per_600": elapsed_ms})
    write_csv(OUT / "raw.csv", raw)
    grouped = defaultdict(list)
    for row in raw:
        grouped[(row["regime"], row["policy"])].append(row)
    summary: dict[str, dict[str, dict[str, float]]] = {}
    for regime in REGIMES:
        summary[regime] = {}
        for policy in POLICIES:
            records = grouped[(regime, policy)]
            summary[regime][policy] = {
                metric: round(statistics.mean(float(r[metric]) for r in records), 7)
                for metric in ("accuracy", "risk_at_80", "coverage", "aurc", "mean_margin", "decision_ms_per_600")
            }
    contrasts = {}
    for regime in REGIMES:
        paired = []
        for seed in SEEDS:
            a = next(r for r in raw if r["regime"] == regime and r["seed"] == seed and r["policy"] == "group_capped")
            b = next(r for r in raw if r["regime"] == regime and r["seed"] == seed and r["policy"] == "weighted")
            paired.append(float(a["risk_at_80"]) - float(b["risk_at_80"]))
        lo, hi = bootstrap_mean_ci(paired)
        contrasts[regime] = {"mean_group_minus_weighted_risk80": round(statistics.mean(paired), 7), "bootstrap95": [round(lo, 7), round(hi, 7)], "seeds": len(paired)}
    # Dedicated single-thread latency and Python allocation benchmark, separate from risk study.
    latency = []
    example = generate_cases(8888, 1000, 0.20)
    weights = fit_reliabilities(generate_cases(7777, 800, 0.20))
    for policy in POLICIES:
        for rep in range(12):
            tracemalloc.start()
            t0 = time.perf_counter_ns()
            for case in example:
                decide(case.votes, weights, policy)
            elapsed_ns = time.perf_counter_ns() - t0
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            latency.append({"policy": policy, "rep": rep, "microseconds_per_decision": elapsed_ns / len(example) / 1000, "tracemalloc_peak_bytes": peak})
    write_csv(OUT / "latency.csv", latency)
    payload = {
        "config": {"seeds": list(SEEDS), "calibration_n": N_CALIBRATION, "test_n": N_TEST,
                   "coverage": 0.8, "regimes": REGIMES, "policies": POLICIES,
                   "provenance": ["provider_A"] * 3 + ["provider_B", "provider_C"],
                   "generator": "3 shared-shock voters (p=0.92 conditional on no shock), 2 independent voters (p=0.82)"},
        "summary": summary, "paired_bootstrap": contrasts,
        "runtime": {"python": sys.version.split()[0], "platform": platform.platform(), "cpu_count_visible": os.cpu_count(),
                    "benchmark_wall_seconds": round(time.perf_counter() - started, 3),
                    "note": "CPU-only; tracemalloc measures Python allocations, not process RSS; timings are descriptive."}
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "risk.svg").write_text(svg_chart(summary), encoding="utf-8")
    print(json.dumps({"experiments": len(raw), "seeds": len(SEEDS), "regimes": list(REGIMES), "paired_bootstrap": contrasts}, indent=2))
    return payload


if __name__ == "__main__":
    run()
