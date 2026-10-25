"""Paired synthetic event-order audit; latent truth is never passed to audit."""

from __future__ import annotations

import csv
import json
import platform
import random
import statistics
import time
import tracemalloc
from dataclasses import asdict
from pathlib import Path

from src.conformance import arbitrary_verdict, audit


def run() -> dict:
    config = json.loads(Path("config.json").read_text())
    rows = []
    inputs = []
    for n in config["trace_lengths"]:
        reference = [f"stage_{i:02}" for i in range(n)]
        for seed in config["seeds"]:
            rng = random.Random(seed)
            for case in range(config["cases_per_scenario"]):
                for scenario in [
                    "ordered_valid",
                    "ordered_invalid",
                    "tied_valid",
                    "tied_invalid",
                    "missing_invalid",
                ]:
                    actual = reference.copy()
                    if scenario in ("ordered_invalid", "tied_invalid"):
                        actual[1], actual[2] = actual[2], actual[1]
                    if scenario == "missing_invalid":
                        actual.pop(1)
                    buckets = [[x] for x in actual]
                    if scenario.startswith("tied"):
                        pair = actual[1:3]
                        rng.shuffle(pair)
                        buckets = [[actual[0]], pair] + [[x] for x in actual[3:]]
                    truth = "conformant" if actual == reference else "nonconformant"
                    # actual order retained only for validation, not used by methods.
                    inputs.append(
                        {
                            "n": n,
                            "seed": seed,
                            "case": case,
                            "scenario": scenario,
                            "reference": reference,
                            "buckets": buckets,
                            "latent_order": actual,
                            "truth": truth,
                        }
                    )
                    timings = {}
                    tracemalloc.start()
                    start = time.perf_counter()
                    result = audit(buckets, reference, config["max_realizations"])
                    timings["bounds"] = time.perf_counter() - start
                    _, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    start = time.perf_counter()
                    arbitrary = arbitrary_verdict(buckets, reference)
                    timings["arbitrary"] = time.perf_counter() - start
                    verdicts = {
                        "arbitrary": arbitrary,
                        "optimistic": "conformant"
                        if result.lower == 0
                        else "nonconformant",
                        "bounds": result.verdict,
                    }
                    for method, verdict in verdicts.items():
                        definite = verdict in ("conformant", "nonconformant")
                        rows.append(
                            {
                                "n": n,
                                "seed": seed,
                                "case": case,
                                "scenario": scenario,
                                "method": method,
                                "truth": truth,
                                "verdict": verdict,
                                "definite": int(definite),
                                "incorrect_definite": int(
                                    definite and verdict != truth
                                ),
                                "seconds": timings.get(method, timings["bounds"]),
                                "python_peak_bytes": peak
                                if method != "arbitrary"
                                else None,
                                "lower": result.lower,
                                "upper": result.upper,
                                "realizations": result.realizations,
                            }
                        )
    out = Path("results")
    out.mkdir(exist_ok=True)
    with (out / "raw.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (out / "event_logs.jsonl").write_text("".join(json.dumps(x) + "\n" for x in inputs))
    summary = []
    for scenario in [
        "all",
        "ordered_valid",
        "ordered_invalid",
        "tied_valid",
        "tied_invalid",
        "missing_invalid",
    ]:
        for method in ["arbitrary", "optimistic", "bounds"]:
            group = [
                r
                for r in rows
                if r["method"] == method
                and (scenario == "all" or r["scenario"] == scenario)
            ]
            errors = sum(r["incorrect_definite"] for r in group)
            decisions = sum(r["definite"] for r in group)
            summary.append(
                {
                    "scenario": scenario,
                    "method": method,
                    "cases": len(group),
                    "definite": decisions,
                    "abstentions": len(group) - decisions,
                    "incorrect_definite": errors,
                    "incorrect_rate": errors / len(group),
                    "decision_rate": decisions / len(group),
                    "selective_error_rate": errors / decisions if decisions else None,
                }
            )
    scaling = []
    for width in range(1, 8):
        reference = ["start"] + [f"s{i}" for i in range(width)] + ["end"]
        groups = [["start"], reference[1:-1], ["end"]]
        elapsed = []
        peaks = []
        for _ in range(5):
            tracemalloc.start()
            start = time.perf_counter()
            r = audit(groups, reference, config["max_realizations"])
            elapsed.append(time.perf_counter() - start)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peaks.append(peak)
        scaling.append(
            dict(
                width=width,
                mean_seconds=statistics.mean(elapsed),
                seconds_se=statistics.stdev(elapsed) / len(elapsed) ** 0.5,
                python_peak_bytes=max(peaks),
                **asdict(r),
            )
        )
    result = {
        "config": config,
        "summary": summary,
        "scaling": scaling,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": __import__("os").cpu_count(),
        },
        "timing_note": "Bounds timed with tracemalloc, arbitrary without. Optimistic reuses bounds computation. Not a fair method-latency comparison; scaling is bounded-audit resource profile.",
    }
    (out / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    all_rows = [r for r in summary if r["scenario"] == "all"]
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="850" height="340" viewBox="0 0 850 340"><rect width="850" height="340" fill="white"/><g font-family="sans-serif" font-size="15" fill="#243746"><text x="30" y="30">Conformance when tied timestamps conceal event order</text><text x="30" y="58">Wrong definite verdicts (red), abstentions (blue), per 100 synthetic cases</text>'
    ]
    for i, r in enumerate(all_rows):
        y = 100 + i * 65
        wrong = r["incorrect_rate"] * 100
        abstain = (1 - r["decision_rate"]) * 100
        svg.append(
            f'<text x="30" y="{y + 18}">{r["method"]}</text><rect x="145" y="{y}" width="{wrong * 8}" height="25" fill="#CC6677"/><rect x="{145 + wrong * 8}" y="{y}" width="{abstain * 8}" height="25" fill="#4477AA"/><text x="{155 + (wrong + abstain) * 8}" y="{y + 19}">wrong {wrong:.1f}; abstain {abstain:.1f}</text>'
        )
    svg.append(
        '<text x="30" y="320">Abstention preserves uncertainty; it does not recover the hidden true order.</text></g></svg>'
    )
    (out / "verdicts.svg").write_text("".join(svg))
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    run()
