"""Paired observationally equivalent worlds and positive-overlap controls."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import random
import statistics
import time
import tracemalloc
from dataclasses import asdict
from pathlib import Path

from src.evaluation import Design, evaluate, interval_decision


def generate(
    n: int, seed: int, design: Design, hidden_reward: float
) -> list[tuple[int, int, float]]:
    rng = random.Random(seed)
    means = ((0.2, 0.6), (0.4, 0.8), (0.5, hidden_reward))
    data = []
    for _ in range(n):
        u = rng.random()
        cumulative = 0.0
        x = len(design.context) - 1
        for candidate, probability in enumerate(design.context):
            cumulative += probability
            if u < cumulative:
                x = candidate
                break
        action = int(rng.random() < design.logging[x][1])
        reward = float(rng.random() < means[x][action])
        data.append((x, action, reward))
    return data


def run() -> dict:
    cfg = json.loads(Path("config.json").read_text())
    rows = []
    cells = []
    examples = []
    for regime in ["deficient", "full_overlap"]:
        design = Design(
            tuple(cfg["context"]),
            (
                (0.5, 0.5),
                (0.5, 0.5),
                (1.0, 0.0) if regime == "deficient" else (0.5, 0.5),
            ),
            tuple(tuple(row) for row in cfg["target"]),
        )
        for n in cfg["sizes"]:
            for seed in cfg["seeds"]:
                paired = []
                for world in [0.0, 1.0]:
                    data = generate(n, seed, design, world)
                    paired.append(data)
                    digest = hashlib.sha256(
                        json.dumps(data, separators=(",", ":")).encode()
                    ).hexdigest()
                    tracemalloc.start()
                    start = time.perf_counter()
                    result = evaluate(design, data, cfg["delta"])
                    elapsed = time.perf_counter() - start
                    _, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    means = ((0.2, 0.6), (0.4, 0.8), (0.5, world))
                    truth = sum(
                        design.context[x] * design.target[x][a] * mean
                        for x, row in enumerate(means)
                        for a, mean in enumerate(row)
                    )
                    known = dict(
                        regime=regime,
                        n=n,
                        seed=seed,
                        world=world,
                        truth=truth,
                        log_sha256=digest,
                        seconds=elapsed,
                        python_peak_bytes=peak,
                        **asdict(result),
                    )
                    cells.append(known)
                    points = {
                        "ips_truncated": result.ips_truncated,
                        "snips_supported": result.snips_supported,
                        "midpoint_imputation": result.midpoint,
                    }
                    for method, value in points.items():
                        if value is None:
                            continue
                        rows.append(
                            {
                                "regime": regime,
                                "n": n,
                                "seed": seed,
                                "world": world,
                                "method": method,
                                "truth": truth,
                                "estimate": value,
                                "lower": None,
                                "upper": None,
                                "covered": None,
                                "width": None,
                                "unsupported_mass": result.unsupported_mass,
                                "decision": "accept"
                                if value > cfg["threshold"]
                                else "reject",
                                "wrong": int(
                                    (value > cfg["threshold"])
                                    != (truth > cfg["threshold"])
                                ),
                                "abstain": 0,
                            }
                        )
                    decision = interval_decision(
                        result.lower, result.upper, cfg["threshold"]
                    )
                    rows.append(
                        {
                            "regime": regime,
                            "n": n,
                            "seed": seed,
                            "world": world,
                            "method": "support_bounds",
                            "truth": truth,
                            "estimate": None,
                            "lower": result.lower,
                            "upper": result.upper,
                            "covered": int(result.lower <= truth <= result.upper),
                            "width": result.upper - result.lower,
                            "unsupported_mass": result.unsupported_mass,
                            "decision": decision,
                            "wrong": int(
                                decision != "abstain"
                                and (decision == "accept") != (truth > cfg["threshold"])
                            ),
                            "abstain": int(decision == "abstain"),
                        }
                    )
                    if n == min(cfg["sizes"]) and seed == cfg["seeds"][0]:
                        examples.append(
                            {"regime": regime, "world": world, "data": data}
                        )
                if regime == "deficient" and paired[0] != paired[1]:
                    raise AssertionError("worlds must have identical observed logs")
    out = Path("results")
    out.mkdir(exist_ok=True)
    with (out / "raw.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (out / "cell_statistics.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in cells)
    )
    (out / "example_logs.json").write_text(json.dumps(examples, indent=2) + "\n")
    summary = []
    for regime in ["deficient", "full_overlap"]:
        for n in cfg["sizes"]:
            for method in [
                "ips_truncated",
                "snips_supported",
                "midpoint_imputation",
                "support_bounds",
            ]:
                group = [
                    r
                    for r in rows
                    if r["regime"] == regime and r["n"] == n and r["method"] == method
                ]
                errors = [
                    r["estimate"] - r["truth"]
                    for r in group
                    if r["estimate"] is not None
                ]
                summary.append(
                    {
                        "regime": regime,
                        "n": n,
                        "method": method,
                        "runs": len(group),
                        "mean_bias": statistics.mean(errors) if errors else None,
                        "rmse": (statistics.mean(e * e for e in errors)) ** 0.5
                        if errors
                        else None,
                        "coverage": statistics.mean(r["covered"] for r in group)
                        if method == "support_bounds"
                        else None,
                        "mean_width": statistics.mean(r["width"] for r in group)
                        if method == "support_bounds"
                        else None,
                        "wrong_decision_rate": statistics.mean(
                            r["wrong"] for r in group
                        ),
                        "decision_rate": 1
                        - statistics.mean(r["abstain"] for r in group),
                    }
                )
    resources = []
    for n in cfg["sizes"]:
        group = [r for r in cells if r["n"] == n]
        resources.append(
            {
                "n": n,
                "mean_seconds": statistics.mean(r["seconds"] for r in group),
                "seconds_se": statistics.stdev(r["seconds"] for r in group)
                / len(group) ** 0.5,
                "max_python_peak_bytes": max(r["python_peak_bytes"] for r in group),
            }
        )
    result = {
        "config": cfg,
        "summary": summary,
        "resources": resources,
        "oracle_identification": {
            "deficient": [
                min(r["truth"] for r in rows if r["regime"] == "deficient"),
                max(r["truth"] for r in rows if r["regime"] == "deficient"),
            ],
            "full_world0": [
                next(
                    r["truth"]
                    for r in rows
                    if r["regime"] == "full_overlap" and r["world"] == 0
                )
            ]
            * 2,
            "full_world1": [
                next(
                    r["truth"]
                    for r in rows
                    if r["regime"] == "full_overlap" and r["world"] == 1
                )
            ]
            * 2,
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": __import__("os").cpu_count(),
        },
        "notes": "Conditional cell-Hoeffding with known design. Worlds paired;320 runs are not independent worlds. No intervals or coverage claimed for point baselines. Resource trace measures evaluator only, excluding generator and output serialization.",
    }
    (out / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="850" height="340" viewBox="0 0 850 340"><rect width="850" height="340" fill="white"/><g font-family="sans-serif" font-size="15" fill="#243746"><text x="30" y="30">OPE under missing action support: same data, different true values</text><text x="30" y="58">Wrong decisions (red), abstentions (blue), per 100 paired runs; n=2000</text>'
    ]
    plot = [
        r for r in summary if r["regime"] == "deficient" and r["n"] == max(cfg["sizes"])
    ]
    for i, r in enumerate(plot):
        y = 85 + i * 48
        wrong = 100 * r["wrong_decision_rate"]
        abstain = 100 * (1 - r["decision_rate"])
        svg.append(
            f'<text x="30" y="{y + 17}">{r["method"]}</text><rect x="230" y="{y}" width="{wrong * 3}" height="22" fill="#CC6677"/><rect x="{230 + wrong * 3}" y="{y}" width="{abstain * 3}" height="22" fill="#4477AA"/><text x="{240 + (wrong + abstain) * 3}" y="{y + 17}">wrong {wrong:.1f}; abstain {abstain:.1f}</text>'
        )
    svg.append(
        '<text x="30" y="320">Structural unknown target mass = 0.40; more logged data cannot remove it.</text></g></svg>'
    )
    (out / "support.svg").write_text("".join(svg))
    width_svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="850" height="380" viewBox="0 0 850 380"><rect width="850" height="380" fill="white"/><g font-family="sans-serif" font-size="15" fill="#243746"><text x="30" y="30">Sampling uncertainty shrinks; missing support remains</text><text x="30" y="58">Mean value interval width across paired worlds and 40 seeds</text><line x1="150" y1="280" x2="680" y2="280" stroke="#8796a5"/><line x1="150" y1="192" x2="680" y2="192" stroke="#666" stroke-dasharray="5 4"/><text x="690" y="197">floor 0.40</text>'
    ]
    for regime, color in [("deficient", "#CC6677"), ("full_overlap", "#4477AA")]:
        group = [
            r
            for r in summary
            if r["regime"] == regime and r["method"] == "support_bounds"
        ]
        points = []
        for i, r in enumerate(group):
            x = 180 + i * 420
            y = 280 - 220 * r["mean_width"]
            points.append(f"{x},{y}")
            width_svg.append(
                f'<circle cx="{x}" cy="{y}" r="5" fill="{color}"/><text x="{x + 10}" y="{y - 10}">{regime}: {r["mean_width"]:.3f}</text>'
            )
        width_svg.append(
            f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2"/>'
        )
    width_svg.append(
        '<text x="165" y="310">n=200</text><text x="580" y="310">n=2000</text><text x="30" y="355">Full overlap permits learning both action values; structural zero probability does not.</text></g></svg>'
    )
    (out / "width.svg").write_text("".join(width_svg))

    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    run()
