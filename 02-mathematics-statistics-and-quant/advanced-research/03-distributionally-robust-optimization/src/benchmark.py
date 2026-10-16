"""Evaluate feasibility, dual gap and a competitive independent primal baseline."""

import csv
import json
import os
from pathlib import Path
import platform
import sys
import time
import tracemalloc
import warnings
from typing import Any
import numpy as np
import scipy
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.kl_robust import Array, kl, mean_variance_approximation, robust_expectation
from src.reference import bernoulli_oracle, slsqp_reference

ROOT = Path(__file__).resolve().parents[1]


def dataset(n: int, seed: int, family: str) -> tuple[Array, Array]:
    rng = np.random.default_rng(seed)
    if family == "bounded":
        p = rng.dirichlet(np.full(n, 3.0))
        loss = rng.uniform(-1, 1, n)
    elif family == "rare_spike":
        p = np.concatenate((0.999 * rng.dirichlet(np.full(n - 1, 3.0)), [0.001]))
        loss = np.concatenate((rng.uniform(0, 0.1, n - 1), [1.0]))
    else:
        raise ValueError("unknown family")
    return p, loss


def write_csv(name: str, rows: list[dict]) -> None:
    with (ROOT / "benchmarks" / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def decision_example(config: dict) -> dict:
    ex = config["decision_example"]
    probability, radius, safe = ex["rare_probability"], ex["radius"], ex["safe_loss"]
    p = np.array([1 - probability, probability])
    loss = np.array([0.0, 1.0])
    result = robust_expectation(p, loss, radius)
    approximate = mean_variance_approximation(p, loss, radius)
    action_losses = np.array([[0.0, 1.0], [safe, safe]])
    exact_action = int(np.argmin([result.value, safe]))
    approximate_action = int(np.argmin([approximate, safe]))
    nominal_action = int(np.argmin([probability, safe]))
    # Two explicit scenarios, not a claim of estimated out-of-sample performance.
    scenarios = []
    for label, true_probability in [("nominal", probability), ("shifted", 0.007)]:
        true_p = np.array([1 - true_probability, true_probability])
        values = action_losses @ true_p
        scenarios.append(
            dict(
                scenario=label,
                true_rare_probability=true_probability,
                kl_to_nominal=kl(true_p, p),
                inside_radius=kl(true_p, p) <= radius,
                nominal_action_loss=float(values[nominal_action]),
                approximate_action_loss=float(values[approximate_action]),
                robust_action_loss=float(values[exact_action]),
                best_action_loss=float(values.min()),
            )
        )
    return dict(
        nominal_risky_loss=probability,
        mean_variance_risky_loss=approximate,
        exact_robust_risky_loss=result.value,
        dual_upper=result.upper,
        binary_oracle=bernoulli_oracle(probability, radius),
        radius=radius,
        safe_loss=safe,
        nominal_action=nominal_action,
        approximate_action=approximate_action,
        robust_action=exact_action,
        action_labels=["risky", "safe"],
        scenarios=scenarios,
    )


def main() -> None:
    config = json.loads((ROOT / "config.json").read_text())
    rows: list[dict[str, Any]] = []
    data = []
    weights = []
    for n in config["sizes"]:
        for family in config["loss_families"]:
            for seed in config["seeds"]:
                p, loss = dataset(n, seed, family)
                data.append(dict(n=n, family=family, seed=seed, p=p.tolist(), loss=loss.tolist()))
                for radius in config["radii"]:
                    start = time.perf_counter()
                    result = robust_expectation(p, loss, radius)
                    root_seconds = time.perf_counter() - start
                    tracemalloc.start()
                    robust_expectation(p, loss, radius)
                    _, root_peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    with warnings.catch_warnings(record=True) as caught:
                        warnings.simplefilter("always")
                        start = time.perf_counter()
                        reference = slsqp_reference(p, loss, radius)
                        slsqp_seconds = time.perf_counter() - start
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        tracemalloc.start()
                        slsqp_reference(p, loss, radius)
                        _, slsqp_peak = tracemalloc.get_traced_memory()
                        tracemalloc.stop()
                    accepted = (
                        reference.success
                        and reference.mass_error <= 1e-8
                        and reference.divergence <= radius + 1e-8
                        and float(reference.q.min()) >= -1e-10
                    )
                    start = time.perf_counter()
                    approximation = mean_variance_approximation(p, loss, radius)
                    approximation_seconds = time.perf_counter() - start
                    tracemalloc.start()
                    mean_variance_approximation(p, loss, radius)
                    _, approx_peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    scale = max(1.0, float(np.ptp(loss)))
                    rows.append(
                        dict(
                            n=n,
                            family=family,
                            seed=seed,
                            radius=radius,
                            nominal=float(p @ loss),
                            robust=result.value,
                            dual_upper=result.upper,
                            scaled_gap=(result.upper - result.value) / scale,
                            kl=result.divergence,
                            kl_violation=max(result.divergence - radius, 0.0),
                            mass_error=abs(float(result.q.sum()) - 1),
                            root_iterations=result.iterations,
                            root_seconds=root_seconds,
                            root_peak_bytes=root_peak,
                            slsqp_value=reference.value,
                            slsqp_success=reference.success,
                            slsqp_accepted=accepted,
                            slsqp_message=reference.message,
                            slsqp_kl=reference.divergence,
                            slsqp_mass_error=reference.mass_error,
                            slsqp_iterations=reference.iterations,
                            slsqp_seconds=slsqp_seconds,
                            slsqp_peak_bytes=slsqp_peak,
                            slsqp_warnings=" | ".join(str(w.message) for w in caught),
                            scaled_slsqp_difference=abs(result.value - reference.value) / scale,
                            approximation=approximation,
                            approximation_signed_error=approximation - result.value,
                            approximation_seconds=approximation_seconds,
                            approximation_peak_bytes=approx_peak,
                        )
                    )
                    weights.append(
                        dict(
                            n=n,
                            family=family,
                            seed=seed,
                            radius=radius,
                            q=result.q.tolist(),
                            slsqp_q=reference.q.tolist(),
                        )
                    )
    write_csv("raw.csv", rows)
    (ROOT / "benchmarks/datasets.json").write_text(json.dumps(data, indent=2) + "\n")
    (ROOT / "benchmarks/weights.json").write_text(json.dumps(weights, indent=2) + "\n")
    binary = []
    for probability in [0.001, 0.1, 0.7]:
        for radius in [0.0, 0.001, 0.01, 0.1, 1.0, 10.0]:
            result = robust_expectation(
                np.array([1 - probability, probability]), np.array([0.0, 1.0]), radius
            )
            oracle = bernoulli_oracle(probability, radius)
            binary.append(
                dict(
                    probability=probability,
                    radius=radius,
                    robust=result.value,
                    oracle=oracle,
                    absolute_error=abs(result.value - oracle),
                )
            )
    write_csv("binary_oracle.csv", binary)
    accepted = [row for row in rows if row["slsqp_accepted"]]
    example = decision_example(config)
    checks = dict(
        max_kl_violation=max(row["kl_violation"] for row in rows),
        max_mass_error=max(row["mass_error"] for row in rows),
        max_scaled_duality_gap=max(abs(row["scaled_gap"]) for row in rows),
        accepted_slsqp_fraction=len(accepted) / len(rows),
        max_scaled_slsqp_difference=max(
            (row["scaled_slsqp_difference"] for row in accepted), default=None
        ),
        max_binary_oracle_error=max(row["absolute_error"] for row in binary),
        rare_approximation_underestimate=example["exact_robust_risky_loss"]
        - example["mean_variance_risky_loss"],
    )
    gate = config["gate"]
    success = (
        checks["max_kl_violation"] <= gate["max_kl_violation"]
        and checks["max_mass_error"] <= gate["max_mass_error"]
        and checks["max_scaled_duality_gap"] <= gate["max_scaled_duality_gap"]
        and checks["accepted_slsqp_fraction"] >= gate["minimum_accepted_slsqp_fraction"]
        and checks["max_scaled_slsqp_difference"] is not None
        and checks["max_scaled_slsqp_difference"]
        <= gate["max_scaled_difference_from_accepted_slsqp"]
        and checks["max_binary_oracle_error"] <= gate["max_binary_oracle_error"]
        and checks["rare_approximation_underestimate"]
        >= gate["minimum_rare_case_approximation_underestimate"]
    )
    summary = []
    for n in config["sizes"]:
        group = [row for row in rows if row["n"] == n]
        summary.append(
            dict(
                n=n,
                cases=len(group),
                slsqp_accepted=sum(row["slsqp_accepted"] for row in group),
                max_gap=max(abs(row["scaled_gap"]) for row in group),
                root_median_ms=1000 * float(np.median([row["root_seconds"] for row in group])),
                slsqp_median_ms=1000 * float(np.median([row["slsqp_seconds"] for row in group])),
                approximation_median_ms=1000
                * float(np.median([row["approximation_seconds"] for row in group])),
                root_peak_bytes=max(row["root_peak_bytes"] for row in group),
                slsqp_peak_bytes=max(row["slsqp_peak_bytes"] for row in group),
            )
        )
    write_csv("summary.csv", summary)
    report = dict(
        success=bool(success),
        checks=checks,
        summary=summary,
        decision=example,
        cases=len(rows),
        approximation_underestimates=sum(row["approximation_signed_error"] < -1e-9 for row in rows),
        approximation_overestimates=sum(row["approximation_signed_error"] > 1e-9 for row in rows),
        rejected_slsqp=[row for row in rows if not row["slsqp_accepted"]],
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
        ["nominal", "mean-variance", "KL worst case", "safe action"],
        [
            example["nominal_risky_loss"],
            example["mean_variance_risky_loss"],
            example["exact_robust_risky_loss"],
            example["safe_loss"],
        ],
    )
    axes[0].set(
        title="Rare event: approximation changes the decision",
        ylabel="Expected loss / robust score",
    )
    axes[0].tick_params(axis="x", labelrotation=25)
    for method, key in [
        ("KL tilt", "root_median_ms"),
        ("SLSQP", "slsqp_median_ms"),
        ("approximation", "approximation_median_ms"),
    ]:
        axes[1].loglog(
            [row["n"] for row in summary], [row[key] for row in summary], "o-", label=method
        )
    axes[1].set(
        title="Observed local costs (different accuracy)",
        xlabel="Number of states",
        ylabel="Median milliseconds",
    )
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(ROOT / "benchmarks/audit.png", dpi=150)
    plt.close(fig)
    print(json.dumps(report, indent=2))
    if not success:
        raise RuntimeError("Predeclared gate failed; outputs retained")


if __name__ == "__main__":
    main()
