"""Synthetic coverage/selection sensitivity for deterministic exposure bounds."""

import csv
import json
import os
import platform
import random
import statistics
import time
import tracemalloc
from dataclasses import asdict
from pathlib import Path
from src.balancing import balanced_split
from src.graph_audit import audit_graph
from src.graph_experiment import corpus
from src.partial_audit import partial_audit

OUT = Path("results/partial1101")


def run() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(Path("config_partial1101.json").read_text())
    raw = []
    for regime in cfg["regimes"]:
        for seed in cfg["seeds"]:
            observed, truth = corpus(seed, regime)
            assignment = balanced_split(observed)
            full = audit_graph(observed, truth, assignment)
            for sampling in ["shuffled", "train_first"]:
                ids = sorted(assignment)
                random.Random(seed + 1101).shuffle(ids)
                if sampling == "train_first":
                    ids.sort(key=lambda rid: assignment[rid] != "train")
                for fraction in cfg["fractions"]:
                    selected = set(ids[: int(len(ids) * fraction)])
                    known = [r for r in truth if r.record_id in selected]
                    tracemalloc.start()
                    start = time.perf_counter_ns()
                    a = partial_audit(observed, known, assignment)
                    elapsed = time.perf_counter_ns() - start
                    _, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    assert (
                        a.lower_exposed_rows
                        <= full.exposed_rows
                        <= a.upper_exposed_rows
                    )
                    raw.append(
                        dict(
                            regime=regime,
                            seed=seed,
                            sampling=sampling,
                            fraction=fraction,
                            **asdict(a),
                            actual_exposed_rows=full.exposed_rows,
                            trivial_upper_rows=(full.exposed_rows if len(known)==len(observed) else len(observed)),
                            elapsed_ns=elapsed,
                            peak_bytes=peak,
                        )
                    )
    with (OUT / "raw.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(raw[0]))
        w.writeheader()
        w.writerows(raw)
    summary = {}
    for sampling in ["shuffled", "train_first"]:
        for fraction in cfg["fractions"]:
            subset = [
                r
                for r in raw
                if r["sampling"] == sampling and r["fraction"] == fraction
            ]
            summary[f"{sampling}:{fraction}"] = {
                "runs": len(subset),
                "mean_width_rows": statistics.mean(
                    r["upper_exposed_rows"] - r["lower_exposed_rows"] for r in subset
                ),
                "mean_trivial_width_rows": statistics.mean(
                    r["trivial_upper_rows"] - r["lower_exposed_rows"] for r in subset
                ),
                "strictly_sharper_runs": sum(
                    r["upper_exposed_rows"] < r["trivial_upper_rows"] for r in subset
                ),
                "detected_runs": sum(r["decision"] == "detected" for r in subset),
                "abstain_runs": sum(r["decision"] == "abstain" for r in subset),
                "conditional_zero_runs": sum(
                    r["decision"] == "conditional-zero" for r in subset
                ),
            }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    scale = []
    for multiplier in cfg["scale_multipliers"]:
        o, t = corpus(0, "missing", multiplier)
        assignment = {
            r.record_id: "train" if i % 2 else "test" for i, r in enumerate(o)
        }
        # Fixed half-coverage; do not run DP beyond its admitted row budget.
        known = t[::2]
        for repeat in range(3):
            tracemalloc.start()
            start = time.perf_counter_ns()
            a = partial_audit(o, known, assignment)
            elapsed = time.perf_counter_ns() - start
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            scale.append(
                dict(rows=a.rows, repeat=repeat, elapsed_ns=elapsed, peak_bytes=peak)
            )
    (OUT / "scale.json").write_text(json.dumps(scale, indent=2) + "\n")
    environment = dict(
        python=platform.python_version(),
        platform=platform.platform(),
        cpu_count=os.cpu_count(),
        cpu_model=next(
            (
                x.split(":", 1)[1].strip()
                for x in Path("/proc/cpuinfo").read_text().splitlines()
                if x.startswith("model name")
            ),
            "unknown",
        ),
    )
    (OUT / "environment.json").write_text(json.dumps(environment, indent=2) + "\n")


if __name__ == "__main__":
    run()
