"""Audit actual legacy outputs against independent rational hinge references."""

import csv
import hashlib
import json
import platform
import random
import statistics
import subprocess
import time
import tracemalloc
from collections.abc import Callable
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

from src.guard import exact_tail, guarded_tail
from src.sources import LEGACY_PATH, ORACLE_PATH, ROOT, SHARED_FIXTURES, legacy, oracle

PROJECT = Path(__file__).resolve().parents[1]
Row = dict[str, Any]


def write_csv(path: Path, rows: list[Row]) -> None:
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fixtures(config: Row) -> list[Row]:
    rows: list[Row] = json.loads(SHARED_FIXTURES.read_text())
    for small in config["weight_exponents"]:
        for large in config["large_weight_exponents"]:
            for loss in config["loss_exponents"]:
                rows.append(
                    {
                        "label": "exponent_sweep",
                        "alpha": config["alpha"],
                        "losses": [10.0**loss, 0.0],
                        "weights": [10.0**small, 10.0**large],
                    }
                )
    tiny = float(np.nextafter(0.0, 1.0))
    rows.append(
        {"label": "unrepresentable_final", "alpha": 0.5, "losses": [0.0, tiny], "weights": [3.0, 1.0]}
    )
    return rows


def accuracy(config: Row, results: Path) -> list[Row]:
    cases = fixtures(config)
    (results / "fixtures.json").write_text(json.dumps(cases, indent=2) + "\n")
    rows: list[Row] = []
    for index, case in enumerate(cases):
        reference: Fraction = oracle.exact_es(case["losses"], case["weights"], case["alpha"])
        rounded = float(reference)
        with np.errstate(under="ignore"):
            baseline = float(legacy.weighted_tail(case["losses"], case["alpha"], case["weights"]).es)
        result = guarded_tail(case["losses"], case["alpha"], case["weights"])
        if result.backend == "fraction":
            assert result.exact_es == reference, f"rational disagreement {index}"
            assert result.es == rounded, f"rounded disagreement {index}"
            assert result.output_rounds_to_zero == (reference != 0 and rounded == 0)
        else:
            assert result.es == baseline, f"ordinary baseline changed {index}"
        rows.append(
            {
                "id": index,
                "label": case["label"],
                "n": len(case["losses"]),
                "alpha": case["alpha"],
                "baseline_es": baseline,
                "guarded_es": result.es,
                "reference_float": rounded,
                "backend": result.backend,
                "fallback_reason": result.fallback_reason or "",
                "baseline_lost_representable": rounded != 0 and baseline == 0,
                "guard_lost_representable": rounded != 0 and result.es == 0,
                "reference_rounds_to_zero": reference != 0 and rounded == 0,
                "output_rounds_to_zero": result.output_rounds_to_zero,
                "baseline_relative_error": abs(baseline / rounded - 1) if rounded else None,
                "guard_relative_error": abs(result.es / rounded - 1) if rounded else None,
                "reference_numerator": str(reference.numerator),
                "reference_denominator": str(reference.denominator),
            }
        )
    assert not any(r["guard_lost_representable"] for r in rows)
    assert all(r["output_rounds_to_zero"] for r in rows if r["reference_rounds_to_zero"])
    write_csv(results / "accuracy.csv", rows)
    return rows


def performance(config: Row, results: Path) -> list[Row]:
    rng = random.Random(config["seed"])
    rows: list[Row] = []
    for n in config["benchmark_n"]:
        for regime in ["ordinary", "tiny_weight"]:
            x = [rng.uniform(-1, 1) for _ in range(n)] if regime == "ordinary" else [1e308] + [0.0] * (n - 1)
            p = (
                [float(rng.randint(1, 8)) for _ in range(n)]
                if regime == "ordinary"
                else [1e-300] + [1e300] * (n - 1)
            )
            methods: dict[str, Callable[[], Any]] = {
                "baseline": lambda: legacy.weighted_tail(x, 0.975, p),
                "guarded": lambda: guarded_tail(x, 0.975, p),
                "always_exact": lambda: exact_tail(x, 0.975, p),
            }
            for function in methods.values():
                function()  # warm-up excluded
            for repeat in range(config["repeats"]):
                order = list(methods)
                rng.shuffle(order)
                for position, method in enumerate(order):
                    function = methods[method]
                    start = time.perf_counter_ns()
                    value = function()
                    ms = (time.perf_counter_ns() - start) / 1e6
                    tracemalloc.start()
                    try:
                        function()
                        _, peak = tracemalloc.get_traced_memory()
                    finally:
                        tracemalloc.stop()
                    rows.append(
                        {
                            "n": n,
                            "regime": regime,
                            "method": method,
                            "repeat": repeat,
                            "order_position": position,
                            "ms": ms,
                            "python_numpy_peak_bytes": peak,
                            "es": value.es,
                            "backend": getattr(value, "backend", "float64"),
                        }
                    )
    write_csv(results / "performance.csv", rows)
    return rows


def figure(accuracy_rows: list[Row], perf: list[Row], path: Path) -> None:
    """Exact categorical SVG for failure counts and fallback time costs."""
    lost = [
        sum(r["baseline_lost_representable"] for r in accuracy_rows),
        sum(r["guard_lost_representable"] for r in accuracy_rows),
    ]
    groups = [("baseline", "#b25335"), ("guarded", "#247e78"), ("always_exact", "#8170a3")]
    n = max(r["n"] for r in perf)
    times = {
        regime: [
            statistics.median(
                r["ms"] for r in perf if r["n"] == n and r["method"] == mode and r["regime"] == regime
            )
            for mode, _ in groups
        ]
        for regime in ["ordinary", "tiny_weight"]
    }
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="420">',
        '<rect width="960" height="420" fill="white"/>',
        '<text x="480" y="28" text-anchor="middle" font-family="sans-serif" font-size="19">'
        "Underflow guard: reliability has a cost</text>",
    ]
    for index, count in enumerate(lost):
        x = 75 + index * 135
        height = count / max(max(lost), 1) * 200
        color = groups[index][1]
        lines.append(f'<rect x="{x}" y="{310 - height}" width="90" height="{height}" fill="{color}"/>')
        lines.append(
            f'<text x="{x + 45}" y="{295 - height}" text-anchor="middle" '
            f'font-family="sans-serif">{count}</text>'
        )
        lines.append(
            f'<text x="{x + 45}" y="335" text-anchor="middle" '
            f'font-family="sans-serif">{groups[index][0]}</text>'
        )
    lines.append(
        '<text x="55" y="60" font-family="sans-serif" font-size="14">Representable ES lost to zero</text>'
    )
    vmax = max(v for vs in times.values() for v in vs) * 1.2
    lines.append(f'<text x="410" y="60" font-family="sans-serif" font-size="14">Median ms; n={n:,}</text>')
    for index, (regime, values) in enumerate(times.items()):
        for j, value in enumerate(values):
            x = 420 + index * 250 + j * 65
            height = value / vmax * 230
            lines.append(
                f'<rect x="{x}" y="{310 - height}" width="50" height="{height}" fill="{groups[j][1]}"/>'
            )
            lines.append(
                f'<text x="{x + 25}" y="{300 - height}" text-anchor="middle" '
                f'font-family="sans-serif" font-size="11">{value:.2f}</text>'
            )
        lines.append(
            f'<text x="{485 + index * 250}" y="335" text-anchor="middle" '
            f'font-family="sans-serif">{regime}</text>'
        )
    for i, (method, color) in enumerate(groups):
        x = 150 + i * 250
        lines.append(f'<rect x="{x}" y="380" width="15" height="12" fill="{color}"/>')
        lines.append(f'<text x="{x + 23}" y="391" font-family="sans-serif" font-size="13">{method}</text>')
    lines.append("</svg>")
    path.write_text("\n".join(lines))


def main() -> None:
    config = json.loads((PROJECT / "benchmarks/config.json").read_text())
    results = PROJECT / "results"
    results.mkdir(exist_ok=True)
    audit = accuracy(config, results)
    perf = performance(config, results)
    figure(audit, perf, results / "comparison.svg")
    summary = {
        "fixtures": len(audit),
        "fallbacks": sum(r["backend"] == "fraction" for r in audit),
        "baseline_lost_representable": sum(r["baseline_lost_representable"] for r in audit),
        "guard_lost_representable": sum(r["guard_lost_representable"] for r in audit),
        "unrepresentable_final": sum(r["reference_rounds_to_zero"] for r in audit),
        "performance_rows": len(perf),
    }
    metadata = {
        "summary": summary,
        "config": config,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_sha256": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [LEGACY_PATH, ORACLE_PATH, SHARED_FIXTURES, PROJECT / "src/guard.py"]
        },
        "cpu": next(
            (
                line
                for line in Path("/proc/cpuinfo").read_text().splitlines()
                if line.startswith("model name")
            ),
            "unknown",
        )
        if Path("/proc/cpuinfo").exists()
        else "unknown",
        "memory_scope": "tracemalloc Python/NumPy allocated peak; not RSS or complete native memory",
        "inference": "synthetic finite distributions, not forecasting/population estimation",
    }
    (results / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    sample = asdict(guarded_tail([1e308, 0.0], weights=[1e-300, 1e300]))
    sample["exact_es"] = str(sample["exact_es"])
    (results / "example.json").write_text(json.dumps(sample, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
