"""Numerical stability audit and a separate prior-predictive calibration experiment."""

from pathlib import Path
import csv
import json
import os
import platform
import sys
import time
import tracemalloc
from typing import Any
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.oracle import Oracle
from src.posterior import Array, posterior

ROOT = Path(__file__).resolve().parents[1]


def operator(d: int, condition: float, seed: int) -> tuple[Array, Array]:
    rng = np.random.default_rng(seed)
    u, _ = np.linalg.qr(rng.normal(size=(d, d)))
    v, _ = np.linalg.qr(rng.normal(size=(d, d)))
    singular = np.geomspace(1.0, 1.0 / condition, d)
    return (u * singular) @ v.T, v


def write_csv(name: str, rows: list[dict]) -> None:
    with (ROOT / "benchmarks" / name).open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def calibration(config: dict) -> list[dict]:
    """Coverage averages over theta~prior and fresh noise, not fixed-parameter coverage."""
    a, v = operator(6, 1e5, config["seed"] + 900000)
    rng = np.random.default_rng(config["seed"] + 900001)
    scenarios = [
        ("correct", 0.001, 1.0),
        ("noise_understated", 0.0001, 1.0),
        ("prior_too_tight", 0.001, 0.1),
    ]
    rows = []
    for replicate in range(config["calibration_replications"]):
        theta = rng.normal(size=6)
        y = a @ theta + rng.normal(scale=0.001, size=6)
        for scenario, sigma, tau in scenarios:
            result = posterior(a, y, sigma, tau)
            for label, direction in [("strong", v[:, 0]), ("weak", v[:, -1])]:
                sd = float(np.sqrt(direction @ result.covariance @ direction))
                error = float(direction @ (result.mean - theta))
                rows.append(
                    dict(
                        replicate=replicate,
                        scenario=scenario,
                        direction=label,
                        assumed_sigma=sigma,
                        assumed_tau=tau,
                        true_sigma=0.001,
                        true_tau=1.0,
                        error=error,
                        posterior_sd=sd,
                        covered_95=abs(error) <= 1.959963984540054 * sd,
                    )
                )
    return rows


def main() -> None:
    config = json.loads((ROOT / "config.json").read_text())
    raw: list[dict[str, Any]] = []
    summary: list[dict[str, Any]] = []
    for di, d in enumerate(config["dimensions"]):
        for ci, condition in enumerate(config["condition_numbers"]):
            a, _ = operator(d, condition, config["seed"] + di * 1000 + ci * 100)
            for ni, sigma in enumerate(config["noise_std"]):
                oracle = Oracle(a, sigma)
                groups: dict[str, list[dict]] = {m: [] for m in config["methods"]}
                for replicate in range(config["replications"]):
                    seed = config["seed"] + di * 100000 + ci * 10000 + ni * 1000 + replicate
                    rng = np.random.default_rng(seed)
                    theta = rng.normal(size=d)
                    y = a @ theta + rng.normal(scale=sigma, size=d)
                    reference = oracle.evaluate(y)
                    for method in config["methods"]:
                        start = time.perf_counter()
                        row: dict[str, Any] = dict(
                            d=d,
                            condition=condition,
                            sigma=sigma,
                            replicate=replicate,
                            seed=seed,
                            method=method,
                            failed=False,
                            failure_reason="",
                            mean_relative_error=None,
                            covariance_relative_error=None,
                            minimum_covariance_eigenvalue=None,
                            seconds=0.0,
                        )
                        try:
                            result = posterior(a, y, sigma, method=method)
                            row["seconds"] = time.perf_counter() - start
                            row["mean_relative_error"] = float(
                                np.linalg.norm(result.mean - reference.mean)
                                / max(float(np.linalg.norm(reference.mean)), 1e-30)
                            )
                            row["covariance_relative_error"] = float(
                                np.linalg.norm(result.covariance - reference.covariance)
                                / np.linalg.norm(reference.covariance)
                            )
                            row["minimum_covariance_eigenvalue"] = float(
                                np.linalg.eigvalsh(result.covariance).min()
                            )
                        except np.linalg.LinAlgError as error:
                            row["failed"] = True
                            row["failure_reason"] = str(error)
                            row["seconds"] = time.perf_counter() - start
                        groups[method].append(row)
                        raw.append(row)
                for method, group in groups.items():
                    valid = [r for r in group if not r["failed"]]
                    tracemalloc.start()
                    try:
                        posterior(a, y, sigma, method=method)
                    except np.linalg.LinAlgError:
                        pass
                    _, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    summary.append(
                        dict(
                            d=d,
                            condition=condition,
                            sigma=sigma,
                            method=method,
                            successful=len(valid),
                            failed=len(group) - len(valid),
                            median_mean_relative_error=float(
                                np.median([r["mean_relative_error"] for r in valid])
                            )
                            if valid
                            else None,
                            max_mean_relative_error=max(r["mean_relative_error"] for r in valid)
                            if valid
                            else None,
                            max_covariance_relative_error=max(
                                r["covariance_relative_error"] for r in valid
                            )
                            if valid
                            else None,
                            median_seconds=float(np.median([r["seconds"] for r in group])),
                            traced_peak_bytes=peak,
                        )
                    )
    write_csv("raw.csv", raw)
    write_csv("summary.csv", summary)
    cal = calibration(config)
    write_csv("calibration_raw.csv", cal)
    cal_summary = []
    for scenario in ["correct", "noise_understated", "prior_too_tight"]:
        for direction in ["strong", "weak"]:
            group = [r for r in cal if r["scenario"] == scenario and r["direction"] == direction]
            coverage = float(np.mean([r["covered_95"] for r in group]))
            n = len(group)
            # Wilson interval for empirical Bernoulli coverage.
            z = 1.959963984540054
            center = (coverage + z * z / (2 * n)) / (1 + z * z / n)
            half = (
                z * np.sqrt(coverage * (1 - coverage) / n + z * z / (4 * n * n)) / (1 + z * z / n)
            )
            cal_summary.append(
                dict(
                    scenario=scenario,
                    direction=direction,
                    replications=n,
                    coverage_95=coverage,
                    coverage_wilson_low=center - half,
                    coverage_wilson_high=center + half,
                    posterior_sd=group[0]["posterior_sd"],
                )
            )
    write_csv("calibration_summary.csv", cal_summary)
    gate = config["gate"]
    selected = [
        s
        for s in summary
        if s["condition"] == gate["condition_number"] and s["sigma"] == gate["noise_std"]
    ]
    checks = []
    for d in config["dimensions"]:
        chosen = {s["method"]: s for s in selected if s["d"] == d}
        svd, normal = chosen["svd"], chosen["normal_equations"]
        improvement = (
            normal["median_mean_relative_error"] / max(svd["median_mean_relative_error"], 1e-30)
            if normal["successful"]
            else None
        )
        checks.append(
            dict(
                d=d,
                improvement_vs_normal=improvement,
                passed=svd["failed"] == 0
                and svd["max_mean_relative_error"] <= gate["max_svd_mean_relative_error"]
                and svd["max_covariance_relative_error"] <= gate["max_svd_cov_relative_error"]
                and (
                    improvement is None
                    or improvement >= gate["min_median_error_improvement_vs_normal"]
                ),
            )
        )
    # Independent, competitive QR method must agree on three deterministic hard-case probes.
    differences = []
    for di, d in enumerate(config["dimensions"]):
        a, _ = operator(d, gate["condition_number"], config["seed"] + di * 1000 + 200)
        y = a @ np.arange(1.0, d + 1.0) / d
        first = posterior(a, y, gate["noise_std"], method="svd")
        second = posterior(a, y, gate["noise_std"], method="augmented_qr")
        differences.append(
            float(np.linalg.norm(first.mean - second.mean) / np.linalg.norm(first.mean))
        )
    success = (
        all(c["passed"] for c in checks)
        and max(differences) <= gate["max_svd_qr_mean_relative_difference"]
    )
    report = dict(
        success=success,
        checks=checks,
        max_svd_qr_difference=max(differences),
        selected=selected,
        calibration=cal_summary,
        environment=dict(
            python=sys.version,
            platform=platform.platform(),
            processor=platform.processor(),
            logical_cpus=os.cpu_count(),
            numpy=np.__version__,
            oracle_decimal_digits=80,
        ),
    )
    (ROOT / "benchmarks/results.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n"
    )
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for method in config["methods"]:
        data = [
            s
            for s in summary
            if s["d"] == 32
            and s["sigma"] == gate["noise_std"]
            and s["method"] == method
            and s["successful"]
        ]
        axes[0].loglog(
            [s["condition"] for s in data],
            [max(s["median_mean_relative_error"], 1e-18) for s in data],
            "o-",
            label=method,
        )
    axes[0].set(
        xlabel="Condition number of A",
        ylabel="Median mean error vs 80-digit oracle",
        title="Numerical stability (d=32)",
    )
    axes[0].legend()
    labels = [f"{r['scenario']}\n{r['direction']}" for r in cal_summary]
    axes[1].bar(range(6), [r["coverage_95"] for r in cal_summary])
    axes[1].axhline(0.95, color="black", linestyle="--")
    axes[1].set_xticks(range(6), labels, rotation=45, ha="right", fontsize=8)
    axes[1].set(
        ylabel="Prior-predictive coverage",
        ylim=(0, 1),
        title="Correct computation cannot repair wrong assumptions",
    )
    fig.tight_layout()
    fig.savefig(ROOT / "benchmarks/audit.png", dpi=150)
    plt.close(fig)
    print(json.dumps(report, indent=2))
    if not success:
        raise RuntimeError("Predeclared gate failed: outputs retained; report failure")


if __name__ == "__main__":
    main()
