"""Paired fault injection experiment with raw outputs and SVG plot."""
from __future__ import annotations

import csv
import json
import math
import os
import platform
import random
import statistics
import tempfile
import time
import tracemalloc
from pathlib import Path

from .engine import InjectedCrash, Mode, STEPS, initialize, inspect, run_job

MODES: tuple[Mode, ...] = ("naive", "split", "atomic")
SEEDS = (11, 23, 37, 41, 59, 67, 71, 83)
JOBS = 80
FAULT_PROBABILITY = 0.65


def faults(seed: int, jobs: int, probability: float) -> list[int | None]:
    if not 0 <= probability <= 1:
        raise ValueError("probability must be between 0 and 1")
    rng = random.Random(seed)
    return [rng.randrange(len(STEPS)) if rng.random() < probability else None
            for _ in range(jobs)]


def trial(mode: Mode, seed: int, jobs: int, probability: float) -> dict[str, float | int | str]:
    if jobs < 1:
        raise ValueError("jobs must be positive")
    schedule = faults(seed, jobs, probability)
    with tempfile.TemporaryDirectory(prefix="durable_mvp_") as tmp:
        path = Path(tmp) / "workflows.sqlite3"
        initialize(path, mode)
        crashes = 0
        recoveries_ms: list[float] = []
        tracemalloc.start()
        start = time.perf_counter_ns()
        for j, fault in enumerate(schedule):
            job_id = f"job-{j:05d}"
            try:
                run_job(path, mode, job_id, fault)
            except InjectedCrash:
                crashes += 1
                recovery_start = time.perf_counter_ns()
                # New SQLite connection is opened inside run_job, emulating restart.
                run_job(path, mode, job_id)
                recoveries_ms.append((time.perf_counter_ns() - recovery_start) / 1e6)
        elapsed_ms = (time.perf_counter_ns() - start) / 1e6
        _, peak_python_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        state = inspect(path)
    expected = jobs * len(STEPS)
    return {"mode": mode, "seed": seed, "jobs": jobs,
            "fault_probability": probability, "injected_crashes": crashes,
            "completed": state["completed"],
            "completion_rate": state["completed"] / jobs,
            "unique_effects": state["unique_effects"],
            "expected_effects": expected,
            "duplicate_effects": state["duplicate_effects"],
            "duplicate_rate": state["duplicate_effects"] / expected,
            "missing_effects": expected - state["unique_effects"],
            "bad_payloads": state["bad_payloads"],
            "elapsed_ms": round(elapsed_ms, 3),
            "ms_per_job": round(elapsed_ms / jobs, 4),
            "recovery_ms_mean": round(statistics.mean(recoveries_ms), 4) if recoveries_ms else 0.0,
            "peak_python_kib": round(peak_python_bytes / 1024, 2)}


def summarize(rows: list[dict[str, float | int | str]], seeds: tuple[int, ...] = SEEDS,
              jobs: int = JOBS, probability: float = FAULT_PROBABILITY) -> dict[str, object]:
    result: dict[str, object] = {"config": {"seeds": list(seeds), "jobs_per_seed": jobs,
        "fault_probability": probability, "python": platform.python_version(),
        "platform": platform.platform(), "cpu_count": os.cpu_count(),
        "sqlite": __import__("sqlite3").sqlite_version,
        "scope": "single-process, local SQLite ACID effects; not remote exactly-once"}}
    metrics: dict[str, object] = {}
    for mode in MODES:
        selected = [r for r in rows if r["mode"] == mode]
        entry: dict[str, object] = {}
        for metric in ("duplicate_rate", "completion_rate", "ms_per_job", "recovery_ms_mean", "peak_python_kib"):
            vals = [float(r[metric]) for r in selected]
            mean = statistics.mean(vals)
            se = statistics.stdev(vals) / math.sqrt(len(vals)) if len(vals) > 1 else 0.0
            entry[metric] = {"mean": round(mean, 6), "ci95_normal": [round(mean - 1.96 * se, 6), round(mean + 1.96 * se, 6)]}
        entry["total_duplicates"] = sum(int(r["duplicate_effects"]) for r in selected)
        entry["total_injected_crashes"] = sum(int(r["injected_crashes"]) for r in selected)
        metrics[mode] = entry
    result["metrics"] = metrics
    result["notes"] = "Normal-approximation CI across 8 seeded scenarios, descriptive only; scenarios not field samples."
    return result


def make_svg(summary: dict[str, object], output: Path) -> None:
    metrics = summary["metrics"]
    bars = []
    for i, mode in enumerate(MODES):
        v = metrics[mode]["duplicate_rate"]["mean"]
        x = 80 + 210 * i
        height = v * 320
        bars.append(f'<rect x="{x}" y="{390-height:.1f}" width="125" height="{height:.1f}" fill="{["#ad4d4d", "#dba344", "#24856a"][i]}"/>')
        bars.append(f'<text x="{x+62}" y="{375-height:.1f}" text-anchor="middle" font-size="18">{v:.1%}</text>')
        bars.append(f'<text x="{x+62}" y="420" text-anchor="middle" font-size="16">{mode}</text>')
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="750" height="470" viewBox="0 0 750 470">'
        '<rect width="750" height="470" fill="white"/>'
        '<text x="35" y="35" font-size="22" font-family="sans-serif">Duplicate effects per expected effect</text>'
        '<line x1="45" y1="390" x2="715" y2="390" stroke="black"/>'
        + ''.join(bars) + '<text x="35" y="457" font-size="12">Synthetic fault injection; local SQLite, 8 paired seeds.</text></svg>')
    output.write_text(svg, encoding="utf-8")


def run(output: Path, seeds: tuple[int, ...] = SEEDS, jobs: int = JOBS,
        probability: float = FAULT_PROBABILITY) -> dict[str, object]:
    output.mkdir(parents=True, exist_ok=True)
    rows = [trial(mode, seed, jobs, probability) for seed in seeds for mode in MODES]
    with (output / "raw.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = summarize(rows, seeds, jobs, probability)
    (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    make_svg(summary, output / "duplicates.svg")
    return summary
