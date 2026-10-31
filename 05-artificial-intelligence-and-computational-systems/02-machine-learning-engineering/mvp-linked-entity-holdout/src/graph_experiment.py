"""Controlled graph misspecification, not empirical entity-resolution quality."""

import csv
import json
import platform
import os
import random
import time
import tracemalloc
from dataclasses import asdict
from pathlib import Path
from src.balancing import balanced_split, count_split
from src.graph_audit import audit_graph
from src.splitter import Record

OUT = Path("results/graph31")


def corpus(
    seed: int, regime: str, multiplier: int = 1
) -> tuple[list[Record], list[Record]]:
    rng = random.Random(seed)
    observed, truth = [], []
    for g, size in enumerate([4, 6, 8, 10]):
        ids = [f"g{g}-r{i}" for i in range(size * multiplier)]
        rng.shuffle(ids)
        for j, rid in enumerate(ids):
            truth.append(Record(rid, (f"t{g}",)))
            if regime == "accurate":
                key = f"o{g}"
            elif regime == "missing":
                key = f"o{g}-{j % 2}"
            elif regime == "overmerged":
                key = f"o{0 if g < 3 else 1}"
            elif regime == "mixed":
                key = f"o{g // 2}-{j % 2}"
            else:
                raise ValueError("unknown regime")
            observed.append(Record(rid, (key,)))
    return observed, truth


def run() -> list[dict[str, object]]:
    OUT.mkdir(parents=True, exist_ok=True)
    config = json.loads(Path("config_graph31.json").read_text())
    rows: list[dict[str, object]] = []
    for regime in config["regimes"]:
        for seed in config["seeds"]:
            observed, truth = corpus(seed, regime)
            for method in ["count30", "balanced30", "truth_oracle"]:
                source = truth if method == "truth_oracle" else observed
                tracemalloc.start()
                t0 = time.perf_counter_ns()
                assignment = (
                    count_split(source, seed=seed)
                    if method == "count30"
                    else balanced_split(source)
                )
                split_ns = time.perf_counter_ns() - t0
                _, split_peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                tracemalloc.start()
                t0 = time.perf_counter_ns()
                a = audit_graph(observed, truth, assignment)
                audit_ns = time.perf_counter_ns() - t0
                _, audit_peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                rows.append(
                    dict(
                        regime=regime,
                        seed=seed,
                        method=method,
                        **asdict(a),
                        deviation_rows=abs(
                            sum(v == "train" for v in assignment.values())
                            - len(truth) / 2
                        ),
                        split_ns=split_ns,
                        split_peak_bytes=split_peak,
                        audit_ns=audit_ns,
                        audit_peak_bytes=audit_peak,
                    )
                )
    with (OUT / "raw.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {}
    for regime in config["regimes"]:
        for method in ["count30", "balanced30", "truth_oracle"]:
            subset = [
                r for r in rows if r["regime"] == regime and r["method"] == method
            ]
            summary[f"{regime}:{method}"] = {
                "runs": len(subset),
                "runs_with_true_leakage": sum(
                    int(r["adjudicated_cuts"]) > 0 for r in subset
                ),
                "mean_exposed_rows": sum(int(r["exposed_rows"]) for r in subset)
                / len(subset),
                "mean_deviation_rows": sum(float(r["deviation_rows"]) for r in subset)
                / len(subset),
                "max_declared_cuts": max(int(r["declared_cuts"]) for r in subset),
            }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (OUT / "environment.json").write_text(
        json.dumps(
            dict(
                python=platform.python_version(),
                machine=platform.machine(),
                platform=platform.platform(),
                processor=platform.processor(),
                cpu_count=os.cpu_count(),
                cpu_model=next(
                    (
                        line.split(":", 1)[1].strip()
                        for line in Path("/proc/cpuinfo").read_text().splitlines()
                        if line.startswith("model name")
                    ),
                    "unknown",
                ),
            ),
            indent=2,
        )
        + "\n"
    )
    # Scale only audit, fixed graph structure; not splitter scalability.
    scaling = []
    for m in [1, 10, 100, 1000]:
        observed, truth = corpus(0, "missing", m)
        assignment = {
            r.record_id: "train" if i % 2 else "test" for i, r in enumerate(observed)
        }
        tracemalloc.start()
        t = time.perf_counter_ns()
        a = audit_graph(observed, truth, assignment)
        elapsed = time.perf_counter_ns() - t
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        scaling.append(dict(rows=a.rows, audit_ns=elapsed, peak_bytes=peak))
    (OUT / "scale.json").write_text(json.dumps(scaling, indent=2) + "\n")
    return rows


if __name__ == "__main__":
    run()
