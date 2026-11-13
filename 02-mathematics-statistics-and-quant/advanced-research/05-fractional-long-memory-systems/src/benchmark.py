"""Reproducible truncation audit: full history is the finite causal reference."""

import csv
import importlib.metadata
import json
import os
import platform
import time
import tracemalloc
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.fractional import Array, apply_filter, budget_memory, coefficient_memory, tail_masses, weights
from src.reference import oracle_filter, prefix_gamma

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmarks"


def write_csv(name: str, rows: list[dict[str, Any]]) -> None:
    with (OUT / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def dataset(family: str, n: int, seed: int) -> Array:
    t = np.arange(n, dtype=float)
    if family == "constant":
        return np.ones(n)
    if family == "sinusoid":
        return np.sin(2 * np.pi * t / 64)
    if family == "pulse":
        x = np.zeros(n)
        x[n // 2] = 1
        return x
    if family == "ar1":
        rng = np.random.default_rng(seed)
        x = np.empty(n)
        x[0] = rng.normal()
        for i in range(1, n):
            x[i] = 0.95 * x[i - 1] + rng.normal()
        return x / np.max(np.abs(x))
    raise ValueError("unknown family")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    config = json.loads((ROOT / "config.json").read_text())
    grid = config["grid"]
    raw = []
    summaries = []
    setups = []
    inputs: dict[str, Any] = {}
    selected_outputs: dict[str, Any] = {}
    for ni, n in enumerate(grid["n"]):
        for fi, family in enumerate(grid["families"]):
            seed = grid["seed"] + ni * 100 + fi
            x = dataset(family, n, seed)
            inputs[f"{family}_{n}"] = x
            scale = max(1.0, float(np.max(np.abs(x))))
            for d in grid["d"]:
                start = time.perf_counter()
                w = weights(d, n)
                generation = time.perf_counter() - start
                start = time.perf_counter()
                tail = tail_masses(w)
                cutoff = coefficient_memory(w, config["coefficient_epsilon"])
                budget = budget_memory(w, config["tail_budget"])
                selection = time.perf_counter() - start
                setups.append(
                    {
                        "n": n,
                        "family": family,
                        "d": d,
                        "weight_seconds": generation,
                        "selection_seconds": selection,
                        "cutoff_memory": cutoff,
                        "budget_memory": budget,
                    }
                )
                full = apply_filter(x, w)
                memories = {
                    "full_direct": n - 1,
                    "full_fft": n - 1,
                    "fixed_32": min(32, n - 1),
                    "fixed_128": min(128, n - 1),
                    "coefficient_cutoff": cutoff,
                    "tail_budget": budget,
                }
                for method in config["methods"]:
                    m = memories[method]
                    engine = "fft" if method == "full_fft" else "direct"
                    for rep in range(grid["timing_repeats"]):
                        start = time.perf_counter()
                        y = apply_filter(x, w, m, method=engine)
                        elapsed = time.perf_counter() - start
                        raw.append(
                            {
                                "family": family,
                                "n": n,
                                "d": d,
                                "seed": seed,
                                "method": method,
                                "memory": m,
                                "retained_coefficients": m + 1,
                                "repeat": rep,
                                "seconds": elapsed,
                            }
                        )
                    error = float(np.max(np.abs(y - full)))
                    bound = float(np.max(np.abs(x)) * tail[m])
                    tracemalloc.start()
                    apply_filter(x, w, m, method=engine)
                    peak = tracemalloc.get_traced_memory()[1]
                    tracemalloc.stop()
                    summaries.append(
                        {
                            "family": family,
                            "n": n,
                            "d": d,
                            "seed": seed,
                            "method": method,
                            "memory": m,
                            "max_abs_error": error,
                            "scaled_error": error / scale,
                            "finite_tail_bound": bound,
                            "scaled_bound": bound / scale,
                            "bound_violation": max(0.0, error - bound) / scale,
                            "median_seconds": float(
                                np.median([r["seconds"] for r in raw[-grid["timing_repeats"] :]])
                            ),
                            "tracked_peak_bytes": peak,
                            "last_value": float(y[-1]),
                            "reference_last_value": float(full[-1]),
                        }
                    )
                    if n == 8192 and d == 0.4 and family == "constant":
                        selected_outputs[method] = y
    oracle = []
    for d in config["oracle"]["d"]:
        for n in config["oracle"]["n"]:
            x = np.random.default_rng(config["oracle"]["seed"] + n).uniform(-1, 1, n)
            w = weights(d, n)
            ref = oracle_filter(x, d)
            oracle.append(
                {
                    "n": n,
                    "d": d,
                    "seed": config["oracle"]["seed"] + n,
                    "max_direct_error": float(np.max(np.abs(apply_filter(x, w) - ref))),
                    "max_fft_error": float(np.max(np.abs(apply_filter(x, w, method="fft") - ref))),
                    "constant_prefix_error": abs(float(np.sum(w)) - prefix_gamma(d, n - 1)),
                }
            )
    adversarial = next(
        r
        for r in summaries
        if r["family"] == "constant"
        and r["n"] == 8192
        and r["d"] == 0.4
        and r["method"] == "coefficient_cutoff"
    )
    pulse = np.zeros(64)
    pulse[-1] = 1
    wp = weights(0.4, 64)
    circular = np.fft.irfft(np.fft.rfft(pulse) * np.fft.rfft(wp), n=64)
    linear = apply_filter(pulse, wp)
    boundary = {
        "circular_first_value": float(circular[0]),
        "linear_first_value": float(linear[0]),
        "max_circular_error": float(np.max(np.abs(circular - linear))),
        "n": 64,
        "d": 0.4,
        "zero_extended_constant_last_at_n8192": prefix_gamma(0.4, 8191),
        "infinite_past_constant_fractional_difference": 0.0,
    }
    checks = {
        "max_fft_scaled_error": max(r["scaled_error"] for r in summaries if r["method"] == "full_fft"),
        "max_tail_bound_violation": max(r["bound_violation"] for r in summaries),
        "max_budget_error": max(r["scaled_error"] for r in summaries if r["method"] == "tail_budget"),
        "max_oracle_scaled_error": max(
            max(r["max_direct_error"], r["max_fft_error"], r["constant_prefix_error"]) for r in oracle
        ),
        "min_cutoff_error_over_epsilon": adversarial["scaled_error"] / config["coefficient_epsilon"],
        "max_constant_bound_gap": max(
            abs(r["max_abs_error"] - r["finite_tail_bound"]) for r in summaries if r["family"] == "constant"
        ),
        "min_circular_wraparound_error": boundary["max_circular_error"],
    }
    passed = {
        key: bool(value >= config["gates"][key] if key.startswith("min_") else value <= config["gates"][key])
        for key, value in checks.items()
    }
    metadata = {
        "date": config["date"],
        "base_commit": config["base_commit"],
        "platform": platform.platform(),
        "cpu": platform.processor(),
        "logical_cpus": os.cpu_count(),
        "python": platform.python_version(),
        "versions": {
            p: importlib.metadata.version(p)
            for p in ["numpy", "scipy", "matplotlib", "mpmath", "pytest", "hypothesis", "ruff", "mypy"]
        },
        "threads": {p: os.getenv(p) for p in ["OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"]},
        "timing_scope": config["timing"],
    }
    write_csv("raw.csv", raw)
    write_csv("summary.csv", summaries)
    write_csv("setup.csv", setups)
    write_csv("oracle.csv", oracle)
    np.savez_compressed(OUT / "inputs.npz", **inputs)
    np.savez_compressed(OUT / "selected_outputs.npz", **selected_outputs)
    results = {
        "checks": checks,
        "passed": passed,
        "scenarios": len(setups),
        "method_results": len(summaries),
        "timed_runs": len(raw),
        "adversarial": adversarial,
        "boundary": boundary,
        "metadata": metadata,
    }
    (OUT / "results.json").write_text(json.dumps(results, indent=2, allow_nan=False) + "\n")
    plot_audit(summaries)
    print(json.dumps({"checks": checks, "passed": passed}, indent=2))
    if not all(passed.values()):
        raise RuntimeError("Predefined gate failed; inspect saved raw evidence")


def plot_audit(summary: list[dict[str, Any]]) -> None:
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6), layout="constrained")
    colors = {
        "coefficient_cutoff": "#B56A20",
        "tail_budget": "#245C83",
        "full_direct": "#586D3D",
        "full_fft": "#245C83",
    }
    for method, marker in (("coefficient_cutoff", "s"), ("tail_budget", "o")):
        selected = [
            r for r in summary if r["family"] == "constant" and r["n"] == 8192 and r["method"] == method
        ]
        axes[0].plot(
            [r["d"] for r in selected],
            [r["max_abs_error"] for r in selected],
            marker=marker,
            color=colors[method],
            label=method,
        )
        axes[1].plot(
            [r["d"] for r in selected],
            [(r["memory"] + 1) / 8192 for r in selected],
            marker=marker,
            color=colors[method],
            label=method,
        )
    axes[0].axhline(0.01, color="#444444", linestyle="--", label="tail-error budget .01")
    axes[0].set(
        xlabel="Fractional order d",
        ylabel="Maximum absolute error",
        title="Unit constant, N=8,192",
        yscale="log",
    )
    axes[0].legend(fontsize=8)
    axes[1].set(
        xlabel="Fractional order d",
        ylabel="Fraction of coefficients retained",
        title="Error control can require long memory",
        ylim=(0, 1),
    )
    axes[1].legend(fontsize=8)
    for method, marker in (("full_direct", "s"), ("full_fft", "o")):
        selected = [r for r in summary if r["family"] == "ar1" and r["d"] == 0.4 and r["method"] == method]
        axes[2].plot(
            [r["n"] for r in selected],
            [1000 * r["median_seconds"] for r in selected],
            marker=marker,
            color=colors[method],
            label=method,
        )
    axes[2].set(
        xlabel="N observations (log)",
        ylabel="Median convolution time, ms (log)",
        title="Full-history numerical baselines",
        xscale="log",
        yscale="log",
    )
    axes[2].set_xticks([256, 2048, 8192], labels=["256", "2,048", "8,192"])
    axes[2].legend(fontsize=8)
    fig.suptitle(
        "Discrete fractional difference audit — small coefficients do not bound accumulated error",
        fontsize=13,
    )
    fig.savefig(OUT / "audit.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
