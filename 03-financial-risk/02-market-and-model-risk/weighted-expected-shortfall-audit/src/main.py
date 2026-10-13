"""Deterministic finite-distribution experiments and measured benchmarks."""

import csv
import hashlib
import json
import platform
import statistics
import subprocess
import time
import tracemalloc
from collections.abc import Callable
from importlib.metadata import version
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
from numpy.typing import NDArray

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.baselines import ROOT, construction_es, historical_es, liquidity_es, strict_tail_es
from src.oracle import lp_es
from src.tail import equal_mass_reference, weighted_tail

PROJECT = Path(__file__).resolve().parents[1]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sample(kind: str, n: int, seed: int) -> tuple[NDArray[np.float64], NDArray[np.float64] | None]:
    rng = np.random.default_rng(seed)
    if kind == "normal":
        return rng.normal(size=n), None
    if kind == "student4":
        return rng.standard_t(4, size=n) / np.sqrt(2), None
    if kind == "discrete_credit":
        return rng.binomial(1, 0.01, size=n).astype(np.float64) * 100.0, None
    x = np.round(rng.standard_t(4, size=n), 1)
    p = rng.lognormal(0, 1.5, size=n)
    return x, p


def benchmark() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for n in [250, 2500, 25000, 250000]:
        x, p = sample("weighted_rounded_t", n, 17)
        funcs: dict[str, Callable[[], float]] = {
            "weighted_exact": lambda: weighted_tail(x, weights=p).es,
            "equal_mass_reference": lambda: equal_mass_reference(x),
            "repo_historical": lambda: historical_es(x, 0.975),
        }
        if n <= 2500:
            funcs["lp_oracle"] = lambda: lp_es(x, weights=p)
        for method, func in funcs.items():
            func()  # warm-up excluded
            for repeat in range(7):
                start = time.perf_counter_ns()
                value = func()
                elapsed = (time.perf_counter_ns() - start) / 1e6
                tracemalloc.start()
                func()
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                rows.append(
                    {
                        "n": n,
                        "method": method,
                        "repeat": repeat,
                        "ms": elapsed,
                        "python_numpy_peak_bytes": peak,
                        "es": value,
                    }
                )
    return rows


def run() -> None:
    results = PROJECT / "results"
    results.mkdir(exist_ok=True)
    config = json.loads((PROJECT / "benchmarks/config.json").read_text())
    alpha = float(config["alpha"])
    methods: dict[str, Callable[[NDArray[np.float64], float], float]] = {
        "repo_historical": historical_es,
        "repo_construction": construction_es,
        "repo_liquidity_fractional": liquidity_es,
        "strict_tail_ablation": strict_tail_es,
    }
    rows: list[dict[str, Any]] = []
    for kind in config["distributions"]:
        for n in config["sample_sizes"]:
            for repeat in range(config["replications"]):
                seed = config["seed"] + repeat + 10000 * n
                x, p = sample(kind, n, seed)
                oracle = lp_es(x, alpha, p)
                estimates = {method: func(x, alpha) for method, func in methods.items()}
                estimates["weighted_exact"] = weighted_tail(x, alpha, p).es
                for method, value in estimates.items():
                    rows.append(
                        {
                            "distribution": kind,
                            "n": n,
                            "replication": repeat,
                            "seed": seed,
                            "method": method,
                            "es": value,
                            "oracle_es": oracle,
                            "abs_error": abs(value - oracle),
                            "valid": bool(np.isfinite(value)),
                        }
                    )
    write_csv(results / "trials.csv", rows)
    summary: list[dict[str, Any]] = []
    for kind in config["distributions"]:
        for method in [*methods, "weighted_exact"]:
            selected = [r for r in rows if r["distribution"] == kind and r["method"] == method]
            errors = [r["abs_error"] for r in selected if r["valid"]]
            summary.append(
                {
                    "distribution": kind,
                    "method": method,
                    "trials": len(selected),
                    "invalid": sum(not r["valid"] for r in selected),
                    "mean_abs_error": statistics.mean(errors) if errors else None,
                    "max_abs_error": max(errors) if errors else None,
                }
            )
    write_csv(results / "summary.csv", summary)
    fixture = np.array([0.0] * 99 + [100.0])
    truth = lp_es(fixture, alpha)
    example = [
        {"method": name, "es": func(fixture, alpha), "reference": truth} for name, func in methods.items()
    ]
    example.append({"method": "weighted_exact", "es": weighted_tail(fixture, alpha).es, "reference": truth})
    write_csv(results / "counterexample.csv", example)
    perf = benchmark()
    write_csv(results / "performance.csv", perf)
    max_error = max(r["abs_error"] for r in rows if r["method"] == "weighted_exact")
    assert max_error <= config["oracle_tolerance"], f"oracle agreement failed: {max_error}"
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    names = ["Historical", "Construction", "Strict tail", "Exact ES"]
    vals = [example[i]["es"] for i in [0, 1, 3, 4]]
    axes[0].bar(names, vals, color=["#a34b35", "#e6a747", "#8776a8", "#267e77"])
    axes[0].axhline(truth, color="black", linestyle="--", label=f"LP reference = {truth:.0f}")
    axes[0].set(ylabel="Loss units", title="99 zero losses + one loss of 100; alpha=0.975")
    axes[0].legend()
    for method in ["weighted_exact", "equal_mass_reference", "repo_historical"]:
        sizes = sorted({r["n"] for r in perf if r["method"] == method})
        medians = [
            statistics.median(r["ms"] for r in perf if r["method"] == method and r["n"] == n) for n in sizes
        ]
        axes[1].loglog(sizes, medians, "o-", label=method)
    axes[1].set(
        xlabel="Scenario count", ylabel="Median time (ms)", title="Timing: unequal-probability scenarios"
    )
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(results / "audit.png", dpi=160)
    plt.close(fig)
    baselines = [
        ROOT / "03-financial-risk/02-market-and-model-risk/var-es-tres-metodos/main.py",
        ROOT / "03-financial-risk/07-financial-and-construction-risk-lab/python/src/risk_models.py",
        ROOT / "03-financial-risk/03-market-liquidity-research/python/laboratorio.py",
        ROOT / "04-quant-strategy-and-products/risk-engines/include/quant/risk.hpp",
    ]
    metadata = {
        "config": config,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_info": next(
            (s for s in Path("/proc/cpuinfo").read_text().splitlines() if s.startswith("model name")),
            "unknown",
        )
        if Path("/proc/cpuinfo").exists()
        else "unknown",
        "packages": {p: version(p) for p in ["numpy", "scipy", "matplotlib", "pytest", "hypothesis"]},
        "repo_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "baseline_sha256": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in baselines
        },
        "max_oracle_abs_error": max_error,
        "memory_scope": "tracemalloc Python/NumPy allocation peak; excludes native LP workspace and RSS",
        "interpretation": "finite-distribution numerical error, not population bias or forecast accuracy",
    }
    (results / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(
        json.dumps(
            {"trials": len(rows), "max_oracle_abs_error": max_error, "counterexample": example}, indent=2
        )
    )


if __name__ == "__main__":
    run()
