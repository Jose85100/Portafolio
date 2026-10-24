"""Paired bounded-retry fault injection across two durable stores."""

from __future__ import annotations

import csv
import json
import platform
import random
import sqlite3
import statistics
import tempfile
import time
import tracemalloc
from pathlib import Path

from src.engine import (
    LostAcknowledgement,
    PayloadConflict,
    apply,
    dispatch,
    enqueue,
    initialize,
    metrics,
)


def run() -> dict:
    config = json.loads(Path("config.json").read_text())
    rows = []
    for n in config["sizes"]:
        for probability in config["ack_loss_probabilities"]:
            for seed in config["seeds"]:
                rng = random.Random(seed)
                schedule = [
                    [
                        rng.random() < probability
                        for _ in range(config["attempt_budget"])
                    ]
                    for _ in range(n)
                ]
                for mode in ("no_dedup", "key_only", "key_hash"):
                    with tempfile.TemporaryDirectory() as tmp:
                        sender = Path(tmp) / "sender.sqlite"
                        provider = Path(tmp) / "provider.sqlite"
                        initialize(sender, provider)
                        tracemalloc.start()
                        start = time.perf_counter()
                        attempts = 0
                        for i, faults in enumerate(schedule):
                            key = f"tenant/effect/{i}"
                            enqueue(sender, key, i + 1)
                            for fault in faults:
                                attempts += 1
                                try:
                                    dispatch(sender, provider, key, mode, fault)
                                except LostAcknowledgement:
                                    continue
                                break
                        elapsed = time.perf_counter() - start
                        _, peak = tracemalloc.get_traced_memory()
                        tracemalloc.stop()
                        values = metrics(sender, provider)
                        size = sender.stat().st_size + provider.stat().st_size
                        # Probe stale semantic requests *after* throughput/effects metrics.
                        rejected = 0
                        for i in range(n):
                            try:
                                apply(provider, f"tenant/effect/{i}", i + 2, mode)
                            except PayloadConflict:
                                rejected += 1
                        rows.append(
                            dict(
                                n=n,
                                ack_loss=probability,
                                seed=seed,
                                mode=mode,
                                attempts=attempts,
                                seconds=elapsed,
                                python_peak_bytes=peak,
                                db_bytes=size,
                                conflicts_rejected=rejected,
                                **values,
                            )
                        )
    out = Path("results")
    out.mkdir(exist_ok=True)
    with (out / "raw.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    summary = []
    for n in config["sizes"]:
        for probability in config["ack_loss_probabilities"]:
            for mode in ("no_dedup", "key_only", "key_hash"):
                group = [
                    r
                    for r in rows
                    if r["n"] == n
                    and r["ack_loss"] == probability
                    and r["mode"] == mode
                ]
                seconds = [r["seconds"] for r in group]
                summary.append(
                    {
                        "n": n,
                        "ack_loss": probability,
                        "mode": mode,
                        "mean_duplicates": statistics.mean(
                            r["duplicates"] for r in group
                        ),
                        "mean_completion": statistics.mean(
                            r["acknowledged"] / n for r in group
                        ),
                        "mean_missing": statistics.mean(
                            r["missing_effects"] for r in group
                        ),
                        "conflict_rejection_rate": statistics.mean(
                            r["conflicts_rejected"] / n for r in group
                        ),
                        "mean_seconds": statistics.mean(seconds),
                        "seconds_se": statistics.stdev(seconds) / len(seconds) ** 0.5,
                        "mean_python_peak_bytes": statistics.mean(
                            r["python_peak_bytes"] for r in group
                        ),
                        "mean_db_bytes": statistics.mean(r["db_bytes"] for r in group),
                    }
                )
    result = {
        "config": config,
        "summary": summary,
        "environment": {
            "python": platform.python_version(),
            "sqlite": sqlite3.sqlite_version,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": __import__("os").cpu_count(),
        },
    }
    (out / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    plot = [
        r for r in summary if r["n"] == max(config["sizes"]) and r["ack_loss"] == 0.35
    ]
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="760" height="330" viewBox="0 0 760 330"><rect width="760" height="330" fill="white"/><g font-family="sans-serif" font-size="15" fill="#243746"><text x="35" y="30">Lost ACK after provider commit: duplicates per 100 jobs</text><text x="35" y="55">8 seeded batches, loss probability 0.35, retry budget 8</text>'
    ]
    for i, r in enumerate(plot):
        y = 100 + i * 65
        value = r["mean_duplicates"]
        svg.append(
            f'<text x="35" y="{y + 18}">{r["mode"]}</text><rect x="165" y="{y}" width="{value * 7}" height="28" fill="{["#CC6677", "#4477AA", "#228833"][i]}"/><text x="{175 + value * 7}" y="{y + 20}">{value:.2f}</text>'
        )
    svg.append(
        '<text x="35" y="315">Zero duplicates alone does not detect changed payloads; key_hash also rejects them.</text></g></svg>'
    )
    (out / "duplicates.svg").write_text("".join(svg))
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    run()
