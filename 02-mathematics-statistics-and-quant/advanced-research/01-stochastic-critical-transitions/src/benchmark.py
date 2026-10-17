"""Deterministic configuration, raw records and descriptive resource benchmarks."""

import csv
import importlib.metadata
import json
import math
import os
import platform
import time
import tracemalloc
from dataclasses import asdict
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.ou import (
    diagnostics,
    euler_transition,
    exact_transition,
    finite_variance,
    simulate,
    stationary_variance,
)
from src.reference import matrix_transition

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "benchmarks"


def write_csv(name: str, rows: list[dict[str, Any]]) -> None:
    with (RESULTS / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def finite_or_none(value: float) -> float | None:
    return float(value) if math.isfinite(value) else None


def run_discretization(config: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    c = config["discretization"]
    for dt in c["dt"]:
        oracle = matrix_transition(c["kappa"], c["sigma"], dt)
        true_variance = finite_variance(oracle, c["steps"])
        for count in c["paths"]:
            for seed in c["seeds"]:
                for method, constructor in (("exact", exact_transition), ("euler", euler_transition)):
                    transition = constructor(c["kappa"], c["sigma"], dt)
                    start = time.perf_counter()
                    z = np.random.default_rng(seed).normal(size=(count, c["steps"] + 1))
                    paths = simulate(transition, z)
                    elapsed = time.perf_counter() - start
                    second = float(np.mean(paths[:, -1] ** 2))
                    expected = finite_variance(transition, c["steps"])
                    # Gaussian E[X^2] standard error, not estimated from a trajectory.
                    standard_error = math.sqrt(2 / count) * expected
                    del paths, z
                    tracemalloc.start()
                    z_memory = np.random.default_rng(seed).normal(size=(count, c["steps"] + 1))
                    memory_paths = simulate(transition, z_memory)
                    peak = tracemalloc.get_traced_memory()[1]
                    tracemalloc.stop()
                    del memory_paths, z_memory
                    rows.append(
                        {
                            "method": method,
                            "dt": dt,
                            "kappa_dt": c["kappa"] * dt,
                            "paths": count,
                            "steps": c["steps"],
                            "horizon": dt * c["steps"],
                            "seed": seed,
                            "phi": transition.phi,
                            "innovation_variance": transition.innovation_variance,
                            "true_second_moment": true_variance,
                            "scheme_second_moment": expected,
                            "sample_second_moment": second,
                            "scheme_relative_bias": (expected - true_variance) / true_variance,
                            "mc_z_within_scheme": (second - expected) / standard_error,
                            "sample_relative_error_vs_ou": (second - true_variance) / true_variance,
                            "stationary_exists": abs(transition.phi) < 1,
                            "seconds_including_rng": elapsed,
                            "tracked_peak_bytes": peak,
                        }
                    )
    return rows


def run_identification(config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    c = config["identification"]
    rows: list[dict[str, Any]] = []
    population = []
    examples = {}
    for index, level in enumerate(c["kappa_levels"]):
        for family in ("slowing", "noise_only"):
            k = level if family == "slowing" else 1.0
            sigma = 1.0 if family == "slowing" else math.sqrt(1 / level)
            transition = exact_transition(k, sigma, c["dt"])
            population.append(
                {
                    "family": family,
                    "level": level,
                    "kappa": k,
                    "sigma": sigma,
                    "variance": stationary_variance(transition),
                    "lag1": transition.phi,
                }
            )
            for length in c["lengths"]:
                # Identical standardized innovations across families at each level.
                # Pairing is deliberate; every row/replicate seed remains reproducible.
                seed = c["seed"] + index * 10000 + length
                z = np.random.default_rng(seed).normal(size=(c["replicates"], length))
                paths = simulate(transition, z, stationary=True)
                moments, phis, rates = diagnostics(paths, c["dt"])
                examples[f"{family}_{level}_{length}"] = paths[0]
                for replicate in range(c["replicates"]):
                    rows.append(
                        {
                            "family": family,
                            "level": level,
                            "length": length,
                            "seed": seed,
                            "replicate": replicate,
                            "true_kappa": k,
                            "true_sigma": sigma,
                            "true_variance": stationary_variance(transition),
                            "true_lag1": transition.phi,
                            "known_mean_second_moment": float(moments[replicate]),
                            "ols_phi": finite_or_none(float(phis[replicate])),
                            "log_rate": finite_or_none(float(rates[replicate])),
                            "euler_rate": finite_or_none(float((1 - phis[replicate]) / c["dt"])),
                            "log_rate_defined": bool(math.isfinite(rates[replicate])),
                        }
                    )
    np.savez_compressed(RESULTS / "example_paths.npz", **examples)
    return rows, population


def plot_audit(
    discrete: list[dict[str, Any]], population: list[dict[str, Any]], summary: list[dict[str, Any]]
) -> None:
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    colors = {"slowing": "#245C83", "noise_only": "#B56A20", "exact": "#245C83", "euler": "#B56A20"}
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), layout="constrained")
    for method, marker in (("exact", "o"), ("euler", "s")):
        selected = [
            r
            for r in discrete
            if r["method"] == method and r["paths"] == 10000 and r["seed"] == discrete[0]["seed"]
        ]
        axes[0].plot(
            [r["kappa_dt"] for r in selected],
            [r["scheme_second_moment"] / r["true_second_moment"] for r in selected],
            marker=marker,
            color=colors[method],
            label=method,
        )
    axes[0].set_yscale("log")
    axes[0].axvline(2, color="#444444", linestyle="--", linewidth=1, label="Euler stability boundary")
    axes[0].set(
        xlabel="Dimensionless step κΔt",
        ylabel="Scheme / OU second moment (log)",
        title="Discretization: 40 steps from zero",
    )
    axes[0].legend(fontsize=8)
    for family, marker, style in (("slowing", "o", "-"), ("noise_only", "s", "--")):
        selected = [r for r in population if r["family"] == family]
        axes[1].plot(
            [1 / r["level"] for r in selected],
            [r["variance"] for r in selected],
            marker=marker,
            linestyle=style,
            color=colors[family],
            label=family,
        )
        selected_s = [r for r in summary if r["family"] == family and r["length"] == 256]
        for row in selected_s:
            axes[2].errorbar(
                1 / row["level"],
                row["phi_median"],
                yerr=[[row["phi_median"] - row["phi_q025"]], [row["phi_q975"] - row["phi_median"]]],
                fmt=marker,
                color=colors[family],
                capsize=3,
            )
        axes[2].plot(
            [1 / r["level"] for r in selected],
            [r["lag1"] for r in selected],
            linestyle=style,
            color=colors[family],
            label=family + " population",
        )
    axes[1].set(
        xlabel="Variance multiplier 1 / level",
        ylabel="Stationary variance",
        title="Variance alone cannot identify slowing",
    )
    axes[1].legend()
    axes[2].set(
        xlabel="Variance multiplier 1 / level",
        ylabel="Lag-1 conditional OLS coefficient",
        title="Finite samples: 256 observations",
    )
    axes[2].legend(fontsize=8)
    fig.suptitle(
        "OU audit — matched variance, different recovery; synthetic known-zero-mean episodes", fontsize=13
    )
    fig.text(
        0.5,
        -0.025,
        "Intervals: empirical 2.5–97.5% replicate quantiles across 200 independent episodes, NOT confidence intervals.",
        ha="center",
        fontsize=9,
    )
    fig.savefig(RESULTS / "audit.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    config = json.loads((ROOT / "config.json").read_text())
    discrete = run_discretization(config)
    raw, population = run_identification(config)
    summary = []
    for family in ("slowing", "noise_only"):
        for level in config["identification"]["kappa_levels"]:
            for length in config["identification"]["lengths"]:
                subset = [
                    r for r in raw if r["family"] == family and r["level"] == level and r["length"] == length
                ]
                phi = np.array([r["ols_phi"] for r in subset], dtype=float)
                rates = np.array([r["log_rate"] for r in subset], dtype=float)
                summary.append(
                    {
                        "family": family,
                        "level": level,
                        "length": length,
                        "replicates": len(subset),
                        "variance_median": float(np.median([r["known_mean_second_moment"] for r in subset])),
                        "phi_median": float(np.nanmedian(phi)),
                        "phi_q025": float(np.nanquantile(phi, 0.025)),
                        "phi_q975": float(np.nanquantile(phi, 0.975)),
                        "kappa_median_valid_only": float(np.nanmedian(rates)),
                        "undefined_rate_count": int(np.isnan(rates).sum()),
                    }
                )
    oracle_rows = []
    for k in [0.01, 0.1, 1, 2]:
        for dt in [1e-8, 0.05, 0.5, 1, 2.5]:
            a, b = exact_transition(k, 1, dt), matrix_transition(k, 1, dt)
            error = max(
                abs(a.phi - b.phi),
                abs(a.innovation_variance - b.innovation_variance) / max(1, b.innovation_variance),
            )
            oracle_rows.append(
                {
                    "kappa": k,
                    "dt": dt,
                    "exact_phi": a.phi,
                    "oracle_phi": b.phi,
                    "exact_q": a.innovation_variance,
                    "oracle_q": b.innovation_variance,
                    "scaled_error": error,
                }
            )
    matched_error = max(
        abs(population[2 * i]["variance"] - population[2 * i + 1]["variance"]) for i in range(4)
    )
    checks = {
        "max_transition_scaled_error": max(r["scaled_error"] for r in oracle_rows),
        "max_variance_match_error": matched_error,
        "max_exact_mc_z": max(abs(r["mc_z_within_scheme"]) for r in discrete if r["method"] == "exact"),
        "min_euler_relative_bias_at_dt1": min(
            r["scheme_relative_bias"] for r in discrete if r["method"] == "euler" and r["dt"] == 1
        ),
        "min_ac1_population_separation_at_kappa01": population[-2]["lag1"] - population[-1]["lag1"],
    }
    gates = config["gates"]
    passed = {
        key: bool(value <= gates[key] if key.startswith("max_") else value >= gates[key])
        for key, value in checks.items()
    }
    cpu_info = Path("/proc/cpuinfo")
    cpu = platform.processor()
    if not cpu and cpu_info.exists():
        cpu = next(
            (
                line.split(":", 1)[1].strip()
                for line in cpu_info.read_text().splitlines()
                if line.startswith("model name")
            ),
            "unreported",
        )
    metadata = {
        "date": config["date"],
        "base_commit": config["base_commit"],
        "platform": platform.platform(),
        "cpu": cpu,
        "logical_cpus": os.cpu_count(),
        "python": platform.python_version(),
        "versions": {
            p: importlib.metadata.version(p)
            for p in [
                "numpy",
                "scipy",
                "matplotlib",
                "nbformat",
                "nbclient",
                "pytest",
                "hypothesis",
                "ruff",
                "mypy",
            ]
        },
        "threads": {p: os.getenv(p) for p in ["OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"]},
        "policy": config["hardware_policy"],
    }
    write_csv("discretization.csv", discrete)
    write_csv("identification.csv", raw)
    write_csv("summary.csv", summary)
    write_csv("population.csv", population)
    write_csv("oracle.csv", oracle_rows)
    (RESULTS / "results.json").write_text(
        json.dumps(
            {
                "checks": checks,
                "passed": passed,
                "discretization_runs": len(discrete),
                "stationary_episodes": len(raw),
                "undefined_rates": sum(not r["log_rate_defined"] for r in raw),
                "metadata": metadata,
            },
            indent=2,
            allow_nan=False,
        )
        + "\n"
    )
    (RESULTS / "transitions.json").write_text(
        json.dumps(
            {"exact_dt1": asdict(exact_transition(1, 1, 1)), "euler_dt1": asdict(euler_transition(1, 1, 1))},
            indent=2,
        )
        + "\n"
    )
    plot_audit(discrete, population, summary)
    print(json.dumps({"checks": checks, "passed": passed}, indent=2))
    if not all(passed.values()):
        raise RuntimeError("predefined gate failed; inspect saved evidence")


if __name__ == "__main__":
    main()
