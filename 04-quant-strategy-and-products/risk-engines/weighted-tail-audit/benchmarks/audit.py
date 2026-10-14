"""Exact rational CVaR oracle, cross-language fixtures, timing and Linux RSS."""

import csv
import hashlib
import importlib.util
import io
import json
import math
import os
import platform
import random
import statistics
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[2]
PYTHON_SOURCE = (
    ROOT / "03-financial-risk/02-market-and-model-risk/weighted-expected-shortfall-audit/src/tail.py"
)
Case = dict[str, Any]


def exact_es(losses: list[float], weights: list[float], alpha: float) -> Fraction:
    """Rockafellar–Uryasev hinge objective at each distinct atom, exact binary inputs.

    No weighted sorting/tail-splitting implementation shared with C++ or Python.
    Fraction(float) preserves the actual IEEE input, not its displayed decimal.
    """
    if not losses or len(losses) != len(weights) or not 0 < alpha < 1:
        raise ValueError("invalid dimensions or confidence")
    if any(not math.isfinite(v) for v in [*losses, *weights]) or any(w < 0 for w in weights):
        raise ValueError("invalid loss or weight")
    x = [Fraction(v) for v, w in zip(losses, weights, strict=True) if w > 0]
    p = [Fraction(w) for w in weights if w > 0]
    if not x:
        raise ValueError("positive mass required")
    total = sum(p, Fraction())
    p = [w / total for w in p]
    mass = 1 - Fraction(alpha)
    return min(
        t + sum((w * max(v - t, Fraction()) for v, w in zip(x, p, strict=True)), Fraction()) / mass
        for t in set(x)
    )


def cases(config: Case) -> list[Case]:
    examples: list[Case] = [
        {"label": "boundary_atom", "alpha": 0.975, "losses": [0.0, 100.0], "weights": [99.0, 1.0]},
        {"label": "negative", "alpha": 0.75, "losses": [-10.0, -2.0, 3.0], "weights": [1.0, 3.0, 2.0]},
        {"label": "zero_weight", "alpha": 0.975, "losses": [0.0, 100.0, 1e9], "weights": [99.0, 1.0, 0.0]},
        {"label": "constant", "alpha": 0.99, "losses": [4.0, 4.0], "weights": [1.0, 3.0]},
        {"label": "large_finite", "alpha": 0.5, "losses": [1e308, 1e308], "weights": [1e308, 1e308]},
        {"label": "signed_cancellation", "alpha": 0.5, "losses": [-1e308, 1e308], "weights": [1.0, 1.0]},
        {"label": "tiny_probability", "alpha": 0.975, "losses": [1e308, 0.0], "weights": [1e-300, 1e300]},
    ]
    rng = random.Random(config["seed"])
    for trial in range(config["fixture_trials"]):
        n = rng.randint(2, config["fixture_max_n"])
        examples.append(
            {
                "label": "seeded_discrete",
                "alpha": config["levels"][trial % 5],
                "losses": [rng.randint(-1000, 1000) / 10 for _ in range(n)],
                "weights": [float(rng.randint(1, 8)) for _ in range(n)],
            }
        )
    return examples


def write_csv(path: Path, rows: list[Case]) -> None:
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def cross_language(binary: Path, config: Case, results: Path) -> list[Case]:
    fixtures = cases(config)
    (results / "fixtures.json").write_text(json.dumps(fixtures, indent=2) + "\n")
    records = []
    for index, case in enumerate(fixtures):
        pairs = " ".join(f"{v!r} {w!r}" for v, w in zip(case["losses"], case["weights"], strict=True))
        records.append(f"{index} {case['alpha']!r} {len(case['losses'])} {pairs}")
    path = results / "fixtures.txt"
    path.write_text("\n".join(records) + "\n")
    cpp = list(
        csv.DictReader(
            io.StringIO(subprocess.check_output([str(binary), "--fixtures", str(path)], text=True))
        )
    )
    if len(cpp) != len(fixtures):
        raise RuntimeError("CLI did not return every fixture")
    spec = importlib.util.spec_from_file_location("repo_python_weighted_tail", PYTHON_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("existing Python source unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    rows = []
    for index, (case, actual) in enumerate(zip(fixtures, cpp, strict=True)):
        if int(actual["id"]) != index:
            raise RuntimeError("fixture ordering mismatch")
        oracle = exact_es(case["losses"], case["weights"], case["alpha"])
        reference = float(oracle)
        es_cpp = float(actual["es"])
        es_python = float(module.weighted_tail(case["losses"], case["alpha"], case["weights"]).es)
        scaled_error = abs(es_cpp - reference) / max(1.0, abs(reference))
        relative_error = abs(es_cpp / reference - 1) if reference != 0 else scaled_error
        if scaled_error > config["scaled_error_tolerance"] or relative_error > 1e-12:
            raise AssertionError(f"C++ oracle disagreement in fixture {index}")
        rows.append(
            {
                "id": index,
                "label": case["label"],
                "n": len(case["losses"]),
                "alpha": case["alpha"],
                "cpp_es": es_cpp,
                "python_es": es_python,
                "exact_es_float": reference,
                "cpp_scaled_error": scaled_error,
                "cpp_relative_error": relative_error,
                "python_scaled_error": abs(es_python - reference) / max(1.0, abs(reference)),
                "python_relative_error": abs(es_python / reference - 1) if reference else 0.0,
                "exact_numerator": str(oracle.numerator),
                "exact_denominator": str(oracle.denominator),
            }
        )
    write_csv(results / "accuracy.csv", rows)
    return rows


def measured_child(command: list[str]) -> tuple[str, int, float]:
    """wait4 reports this child's peak RSS; no inherited RUSAGE_CHILDREN maximum.

    Linux ru_maxrss is KiB. RSS includes dataset, runtime and warm-up, not just kernel.
    """
    start = time.perf_counter()
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
        assert process.stdout is not None and process.stderr is not None
        stdout = process.stdout.read()
        stderr = process.stderr.read()
        _, status, usage = os.wait4(process.pid, 0)
        process.returncode = os.waitstatus_to_exitcode(status)
        if process.returncode:
            raise RuntimeError(f"benchmark child failed: {stderr}")
    return stdout, int(usage.ru_maxrss), (time.perf_counter() - start) * 1000


def performance(binary: Path, config: Case, results: Path) -> list[Case]:
    rows: list[Case] = []
    for n in config["benchmark_n"]:
        outputs: dict[str, float] = {}
        for mode in ["weighted", "expanded", "uniform_ablation"]:
            output, rss, process_ms = measured_child(
                [
                    str(binary),
                    "--bench",
                    mode,
                    str(n),
                    str(config["benchmark_repeats"]),
                    str(config["seed"]),
                    "--csv",
                ]
            )
            part = list(csv.DictReader(io.StringIO(output)))
            outputs[mode] = float(part[0]["es"])
            for row in part:
                rows.append(
                    {
                        "n": int(row["n"]),
                        "mode": mode,
                        "repeat": int(row["repeat"]),
                        "kernel_ms": float(row["ms"]),
                        "es": float(row["es"]),
                        "self_peak_rss_kib": int(row["self_peak_rss_kib"]),
                        "wait4_peak_rss_kib": rss,
                        "process_total_ms": process_ms,
                    }
                )
        if abs(outputs["weighted"] - outputs["expanded"]) > 1e-9:
            raise AssertionError("weighted vs expanded measure mismatch")
    write_csv(results / "performance.csv", rows)
    return rows


def figure(rows: list[Case], output: Path) -> None:
    """Dependency-free SVG chart with measured timing and process RSS."""
    sizes = sorted({r["n"] for r in rows})
    panels = [
        ("kernel_ms", "Median algorithm time (ms)", 50),
        ("self_peak_rss_kib", "Process peak RSS (MiB)", 490),
    ]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="430" viewBox="0 0 960 430">',
        '<rect width="960" height="430" fill="white"/>',
        '<text x="480" y="25" text-anchor="middle" font-family="sans-serif" font-size="19">'
        "Weighted ES vs equivalent expanded baseline</text>",
    ]
    colors = {"weighted": "#247c77", "expanded": "#bb593a", "uniform_ablation": "#8770a3"}

    def x_position(n: int, left: int, width: int) -> float:
        return left + width * (math.log10(n) - math.log10(sizes[0])) / (
            math.log10(sizes[-1]) - math.log10(sizes[0])
        )

    for metric, title, left in panels:
        top, width, height = 75, 370, 265
        values = {
            mode: [
                statistics.median(r[metric] for r in rows if r["n"] == n and r["mode"] == mode)
                / (1024 if metric.endswith("kib") else 1)
                for n in sizes
            ]
            for mode in colors
        }
        vmax = max(v for vs in values.values() for v in vs) * 1.1
        lines.append(f'<text x="{left}" y="55" font-family="sans-serif" font-size="15">{title}</text>')
        for tick in range(5):
            y = top + height - tick * height / 4
            lines.append(f'<path d="M{left},{y}h{width}" stroke="#ddd"/>')
            lines.append(
                f'<text x="{left - 5}" y="{y + 4}" text-anchor="end" '
                f'font-family="sans-serif" font-size="11">{vmax * tick / 4:.1f}</text>'
            )
        for n in sizes:
            x = x_position(n, left, width)
            lines.append(
                f'<text x="{x}" y="360" text-anchor="middle" '
                f'font-family="sans-serif" font-size="11">{n:,}</text>'
            )
        for mode, color in colors.items():
            points = " ".join(
                f"{x_position(sizes[i], left, width)},{top + height - v / vmax * height}"
                for i, v in enumerate(values[mode])
            )
            lines.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"/>')
    for i, (mode, color) in enumerate(colors.items()):
        x = 100 + i * 280
        lines.append(f'<rect x="{x}" y="390" width="15" height="12" fill="{color}"/>')
        lines.append(f'<text x="{x + 22}" y="401" font-family="sans-serif" font-size="13">{mode}</text>')
    lines.append(
        '<text x="480" y="379" text-anchor="middle" font-family="sans-serif" font-size="11">'
        "Scenario count (log scale)</text>"
    )
    lines.append("</svg>")
    output.write_text("\n".join(lines))


def run() -> None:
    if sys.platform != "linux":
        raise RuntimeError("MVP reproduction currently requires Linux for per-process RSS")
    config = json.loads((PROJECT / "benchmarks/config.json").read_text())
    results = PROJECT / "results"
    results.mkdir(exist_ok=True)
    binary = PROJECT / "build/release/weighted_tail_cli"
    accuracy = cross_language(binary, config, results)
    perf = performance(binary, config, results)
    figure(perf, results / "comparison.svg")
    paths = [
        PROJECT.parent / "include/quant/risk.hpp",
        PYTHON_SOURCE,
        PROJECT.parent / "include/quant/weighted_tail.hpp",
    ]
    metadata = {
        "config": config,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "compiler": subprocess.check_output(["g++", "--version"], text=True).splitlines()[0],
        "numeric_platform": json.loads(subprocess.check_output([str(binary), "--platform"], text=True)),
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_sha256": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths
        },
        "fixtures": len(accuracy),
        "performance_rows": len(perf),
        "max_cpp_scaled_error": max(r["cpp_scaled_error"] for r in accuracy),
        "max_cpp_relative_error": max(r["cpp_relative_error"] for r in accuracy),
        "rss_scope": "C++ /proc/self/status VmHWM after exec, includes dataset/runtime/warm-up; KiB",
        "wait4_scope": "Raw fork-inherited maxima also preserved; not used as kernel memory",
        "timing_scope": "C++ steady_clock, includes allocation/copy/expansion/sort, excludes CLI/startup",
        "cpu": next(s for s in Path("/proc/cpuinfo").read_text().splitlines() if s.startswith("model name")),
    }
    (results / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: metadata[k]
                for k in ["fixtures", "performance_rows", "max_cpp_scaled_error", "max_cpp_relative_error"]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    run()
