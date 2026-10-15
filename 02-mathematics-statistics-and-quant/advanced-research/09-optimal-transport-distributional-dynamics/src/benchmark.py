"""Audit feasibility before interpreting a transport cost as an approximation."""

import csv
import json
import os
from pathlib import Path
import platform
import sys
import time
import tracemalloc
from typing import Any
import numpy as np
import scipy
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.reference import linear_program, monotone_w2_squared
from src.transport import Array, residual, sinkhorn

ROOT = Path(__file__).resolve().parents[1]


def dataset(n: int, scenario: str, seed: int) -> tuple[Array, Array, Array, Array]:
    rng = np.random.default_rng(seed)
    if scenario == "overlap":
        x = np.sort(rng.normal(0, 0.2, n))
        y = np.sort(rng.normal(0.3, 0.2, n))
        a = rng.dirichlet(np.full(n, 3.0))
        b = rng.dirichlet(np.full(n, 3.0))
    elif scenario == "separated":
        x = np.linspace(0, 1, n, dtype=np.float64)
        y = x + 20
        a = np.full(n, 1.0 / n)
        b = a.copy()
    elif scenario == "mass_mismatch":
        x = np.linspace(0, 1, n, dtype=np.float64)
        y = x.copy()
        a = np.full(n, 0.1 / (n - 1))
        a[0] = 0.9
        b = np.full(n, 0.1 / (n - 1))
        b[-1] = 0.9
    else:
        raise ValueError("unknown dataset")
    return x, y, a, b


def csv_file(name: str, rows: list[dict]) -> None:
    with (ROOT / "benchmarks" / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def adversarial() -> dict:
    a, b = np.array([0.9, 0.1]), np.array([0.1, 0.9])
    cost = np.array([[0.0, 1.0], [1.0, 0.0]])
    truth, _ = linear_program(a, b, cost)
    result = sinkhorn(a, b, cost, 0.01, max_iterations=1)
    np.savez(
        ROOT / "benchmarks/adversarial_plans.npz",
        a=a,
        b=b,
        cost=cost,
        raw=result.raw_plan,
        rounded=result.plan,
    )
    return dict(
        reference=truth,
        raw_cost=result.raw_cost,
        rounded_cost=result.upper,
        raw_residual=result.raw_residual,
        rounded_residual=result.rounded_residual,
        lower=result.lower,
        converged=result.converged,
        raw_plan=result.raw_plan.tolist(),
        rounded_plan=result.plan.tolist(),
    )


def main() -> None:
    config = json.loads((ROOT / "config.json").read_text())
    raw: list[dict[str, Any]] = []
    refs = []
    manifest = []
    for n in config["sizes"]:
        for scenario in config["scenarios"]:
            # Separated/mismatch cases are deterministic: no duplicate replicas.
            seeds = config["seeds"] if scenario == "overlap" else [config["seeds"][0]]
            for seed in seeds:
                x, y, a, b = dataset(n, scenario, seed)
                cost = (x[:, None] - y[None, :]) ** 2
                start = time.perf_counter()
                reference, plan = linear_program(a, b, cost)
                seconds = time.perf_counter() - start
                start = time.perf_counter()
                monotone = monotone_w2_squared(x, y, a, b)
                monotone_seconds = time.perf_counter() - start
                refs.append(
                    dict(
                        n=n,
                        scenario=scenario,
                        seed=seed,
                        lp_cost=reference,
                        monotone_cost=monotone,
                        relative_discrepancy=abs(reference - monotone) / max(1.0, abs(reference)),
                        lp_seconds=seconds,
                        monotone_seconds=monotone_seconds,
                        lp_residual=residual(plan, a, b),
                    )
                )
                manifest.append(
                    dict(
                        n=n,
                        scenario=scenario,
                        seed=seed,
                        x=x.tolist(),
                        y=y.tolist(),
                        a=a.tolist(),
                        b=b.tolist(),
                    )
                )
                for epsilon in config["epsilons"]:
                    for method in config["methods"]:
                        row: dict[str, Any] = dict(
                            n=n,
                            scenario=scenario,
                            seed=seed,
                            epsilon=epsilon,
                            method=method,
                            failed=False,
                            failure_reason="",
                            reference=reference,
                            raw_cost=None,
                            upper=None,
                            lower=None,
                            relative_cost_error=None,
                            raw_residual=None,
                            rounded_residual=None,
                            gap=None,
                            iterations=None,
                            converged=False,
                            seconds=None,
                            traced_peak_bytes=None,
                        )
                        start = time.perf_counter()
                        try:
                            result = sinkhorn(
                                a,
                                b,
                                cost,
                                epsilon,
                                method,
                                config["max_iterations"],
                                config["tolerance"],
                            )
                            row.update(
                                raw_cost=result.raw_cost,
                                upper=result.upper,
                                lower=result.lower,
                                raw_residual=result.raw_residual,
                                rounded_residual=result.rounded_residual,
                                gap=result.upper - result.lower,
                                iterations=result.iterations,
                                converged=result.converged,
                                relative_cost_error=abs(result.upper - reference)
                                / max(abs(reference), 1e-15),
                            )
                        except (FloatingPointError, OverflowError) as error:
                            row.update(failed=True, failure_reason=str(error))
                        row["seconds"] = time.perf_counter() - start
                        tracemalloc.start()
                        try:
                            sinkhorn(
                                a,
                                b,
                                cost,
                                epsilon,
                                method,
                                config["max_iterations"],
                                config["tolerance"],
                            )
                        except (FloatingPointError, OverflowError):
                            pass
                        _, row["traced_peak_bytes"] = tracemalloc.get_traced_memory()
                        tracemalloc.stop()
                        raw.append(row)
    csv_file("raw.csv", raw)
    csv_file("references.csv", refs)
    (ROOT / "benchmarks/datasets.json").write_text(json.dumps(manifest, indent=2) + "\n")
    adverse = adversarial()
    good = [r for r in raw if r["method"] == "log" and not r["failed"]]
    bound_violation = max(
        max(r["lower"] - r["reference"], r["reference"] - r["upper"], 0.0)
        / max(1.0, abs(r["reference"]))
        for r in good
    )
    separated = [
        r for r in good if r["scenario"] == "separated" and r["epsilon"] == min(config["epsilons"])
    ]
    naive_failures = [
        r
        for r in raw
        if r["method"] == "naive"
        and r["scenario"] == "separated"
        and r["epsilon"] == min(config["epsilons"])
    ]
    checks = dict(
        log_all_finite=len(good) == len(raw) // 2,
        max_rounded_residual=max(r["rounded_residual"] for r in good),
        max_reference_discrepancy=max(r["relative_discrepancy"] for r in refs),
        max_scaled_bound_violation=bound_violation,
        max_separated_relative_cost_error=max(r["relative_cost_error"] for r in separated),
        naive_failed_all_selected=all(r["failed"] for r in naive_failures),
        false_low_cost_detected=adverse["raw_cost"] < adverse["reference"] - 0.1
        and adverse["raw_residual"] > 0.1,
    )
    gate = config["gate"]
    success = (
        checks["log_all_finite"]
        and checks["max_rounded_residual"] <= gate["max_rounded_marginal_residual"]
        and checks["max_reference_discrepancy"] <= gate["max_reference_relative_discrepancy"]
        and checks["max_scaled_bound_violation"] <= gate["max_bound_violation_scaled"]
        and checks["max_separated_relative_cost_error"] <= gate["max_separated_relative_cost_error"]
        and checks["naive_failed_all_selected"]
        and checks["false_low_cost_detected"]
    )
    selected = [
        r
        for r in raw
        if r["n"] == 64
        and r["seed"] == config["seeds"][0]
        and r["epsilon"] == min(config["epsilons"])
    ]
    summary = []
    for method in config["methods"]:
        group = [r for r in raw if r["method"] == method]
        valid = [r for r in group if not r["failed"]]
        summary.append(
            dict(
                method=method,
                total=len(group),
                failed=len(group) - len(valid),
                nonconverged=sum(not r["converged"] for r in valid),
                max_raw_residual=max(r["raw_residual"] for r in valid),
                max_rounded_residual=max(r["rounded_residual"] for r in valid),
            )
        )
    csv_file("summary.csv", summary)
    self_mass = np.array([0.5, 0.5])
    self_cost = np.array([[0.0, 1.0], [1.0, 0.0]])
    self_result = sinkhorn(self_mass, self_mass, self_cost, 1.0)
    report = dict(
        self_bias=dict(
            epsilon=1.0, regularized_transport_cost=self_result.upper, exact_w2_squared=0.0
        ),
        success=bool(success),
        checks=checks,
        summary=summary,
        selected=selected,
        adversarial=adverse,
        dataset_count=len(refs),
        raw_rows=len(raw),
        environment=dict(
            python=sys.version,
            platform=platform.platform(),
            processor=platform.processor(),
            logical_cpus=os.cpu_count(),
            numpy=np.__version__,
            scipy=scipy.__version__,
            blas_threads=os.environ.get("OPENBLAS_NUM_THREADS"),
        ),
    )
    (ROOT / "benchmarks/results.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n"
    )
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].bar(
        ["raw cost", "repaired cost", "LP optimum"],
        [adverse["raw_cost"], adverse["rounded_cost"], adverse["reference"]],
    )
    axes[0].set(title="One iteration: low cost can be infeasible", ylabel="Transport cost")
    for scenario in config["scenarios"]:
        group = sorted(
            [
                r
                for r in good
                if r["n"] == 64 and r["seed"] == config["seeds"][0] and r["scenario"] == scenario
            ],
            key=lambda r: r["epsilon"],
        )
        axes[1].loglog(
            [r["epsilon"] for r in group],
            [max(r["relative_cost_error"], 1e-16) for r in group],
            "o-",
            label=scenario,
        )
    axes[1].set(
        title="Rounded log-Sinkhorn vs LP (n=64)", xlabel="epsilon", ylabel="Relative cost error"
    )
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(ROOT / "benchmarks/audit.png", dpi=150)
    plt.close(fig)
    print(json.dumps(report, indent=2))
    if not success:
        raise RuntimeError("Predeclared gate failed; evidence retained")


if __name__ == "__main__":
    main()
