"""Raw finite-threshold, asymptotic and Monte Carlo evidence, with fixed gates."""

import csv
import importlib.metadata
import json
import os
import platform
import statistics
import time
import tracemalloc
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import kendalltau

from src.copulas import Copula, asymptotic_lambda, conditional, direct, kendall_tau, sample_latent
from src.reference import conditional_second_moment, latent_coordinate_reference, tail_coordinate_reference

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmarks"


def write_csv(name: str, rows: list[dict[str, Any]]) -> None:
    with (OUT / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run_grid(config: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for spec in config["grid"]["models"]:
        for rho in config["grid"]["rho"]:
            model = Copula(rho, spec["df"])
            for q in config["grid"]["q"]:
                a, ae = tail_coordinate_reference(model, q)
                b, be = latent_coordinate_reference(model, q)
                second = conditional_second_moment(model, q)
                cm_variance = second - a * a
                direct_variance = a / (1 - q) - a * a
                variance_ratio_bound = (1 - q) * (1 - a) / (1 - (1 - q) * a)
                rows.append(
                    {
                        "model": spec["name"],
                        "df": spec["df"],
                        "rho": rho,
                        "q": q,
                        "kendall_tau": kendall_tau(model),
                        "finite_lambda": a,
                        "joint_probability": (1 - q) * a,
                        "latent_reference": b,
                        "coordinate_disagreement": abs(a - b),
                        "quad_error_tail": ae,
                        "quad_error_latent": be,
                        "asymptotic_lambda": asymptotic_lambda(model),
                        "finite_minus_limit": a - asymptotic_lambda(model),
                        "conditional_variance_per_draw": cm_variance,
                        "direct_variance_per_draw": direct_variance,
                        "variance_ratio": cm_variance / direct_variance,
                        "variance_ratio_bound": variance_ratio_bound,
                        "variance_bound_violation": max(
                            0.0, cm_variance / direct_variance - variance_ratio_bound
                        ),
                    }
                )
    return rows


def run_mc(
    config: dict[str, Any], grid: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = []
    memory = []
    c = config["monte_carlo"]
    for mi, spec in enumerate(c["models"]):
        model = Copula(c["rho"], spec["df"])
        for qi, q in enumerate(c["q"]):
            reference = next(
                r["finite_lambda"]
                for r in grid
                if r["model"] == spec["name"] and r["rho"] == c["rho"] and r["q"] == q
            )
            for n in c["n"]:
                for method_index, (name, estimator) in enumerate(
                    (("direct", direct), ("conditional", conditional))
                ):
                    for rep in range(c["replicates"]):
                        components = [c["seed"], mi, qi, n, method_index, rep]
                        start = time.perf_counter()
                        result = estimator(
                            model, q, n, np.random.default_rng(np.random.SeedSequence(components))
                        )
                        elapsed = time.perf_counter() - start
                        estimate = result["estimate"]
                        assert estimate is not None
                        rows.append(
                            {
                                "model": spec["name"],
                                "rho": model.rho,
                                "df": model.df,
                                "q": q,
                                "n": n,
                                "replicate": rep,
                                "method": name,
                                "seed_components": json.dumps(components),
                                "finite_reference": reference,
                                "estimate": estimate,
                                "error": estimate - reference,
                                "joint_count": result.get("joint_count"),
                                "marginal_count": result.get("marginal_count"),
                                "random_denominator_estimate": result.get("random_denominator_estimate"),
                                "conditional_sample_se": result.get("sample_se"),
                                "seconds_including_rng": elapsed,
                            }
                        )
                    tracemalloc.start()
                    estimator(
                        model,
                        q,
                        n,
                        np.random.default_rng(
                            np.random.SeedSequence([c["seed"], mi, qi, n, method_index, 0])
                        ),
                    )
                    peak = tracemalloc.get_traced_memory()[1]
                    tracemalloc.stop()
                    memory.append(
                        {
                            "model": spec["name"],
                            "q": q,
                            "n": n,
                            "method": name,
                            "tracked_peak_bytes": peak,
                            "replicate_replayed_for_memory": 0,
                        }
                    )
    return rows, memory


def summarize(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary = []
    keys = sorted({(r["model"], r["q"], r["n"], r["method"]) for r in raw})
    for model, q, n, method in keys:
        selected = [r for r in raw if (r["model"], r["q"], r["n"], r["method"]) == (model, q, n, method)]
        errors = np.array([r["error"] for r in selected])
        estimates = np.array([r["estimate"] for r in selected])
        rmse = float(np.sqrt(np.mean(errors**2)))
        seconds = statistics.mean(r["seconds_including_rng"] for r in selected)
        summary.append(
            {
                "model": model,
                "q": q,
                "n": n,
                "method": method,
                "replicates": len(selected),
                "reference": selected[0]["finite_reference"],
                "mean_estimate": float(np.mean(estimates)),
                "bias": float(np.mean(errors)),
                "rmse": rmse,
                "relative_rmse": rmse / selected[0]["finite_reference"],
                "replicate_q025": float(np.quantile(estimates, 0.025)),
                "replicate_q975": float(np.quantile(estimates, 0.975)),
                "zero_joint_fraction": sum(r["joint_count"] == 0 for r in selected) / len(selected)
                if method == "direct"
                else None,
                "undefined_random_denominator": sum(r["marginal_count"] == 0 for r in selected)
                if method == "direct"
                else None,
                "mean_seconds": seconds,
                "time_times_mse_proxy": seconds * rmse**2,
            }
        )
    return summary


def plot_results(grid: list[dict[str, Any]], summary: list[dict[str, Any]]) -> None:
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    colors = {"gaussian": "#245C83", "t4": "#B56A20", "t30": "#586D3D"}
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), layout="constrained")
    for model, marker in (("gaussian", "o"), ("t4", "s"), ("t30", "^")):
        selected = [r for r in grid if r["rho"] == 0.5 and r["model"] == model]
        x = [-np.log10(1 - r["q"]) for r in selected]
        axes[0].plot(
            x, [r["finite_lambda"] for r in selected], marker=marker, color=colors[model], label=model
        )
        axes[0].axhline(selected[0]["asymptotic_lambda"], color=colors[model], linestyle="--", linewidth=1)
    axes[0].set(
        xlabel="−log₁₀ marginal exceedance probability",
        ylabel="P(V>q | U>q)",
        title="Same Kendall τ=1/3, different joint tails",
        xticks=[1, 2, 3, 4],
    )
    axes[0].legend(title="Dashed: asymptotic limits", fontsize=9)
    for method, marker, color in (("direct", "o", "#245C83"), ("conditional", "s", "#B56A20")):
        selected = [r for r in summary if r["model"] == "t4" and r["q"] == 0.999 and r["method"] == method]
        axes[1].plot(
            [r["n"] for r in selected],
            [100 * r["relative_rmse"] for r in selected],
            marker=marker,
            color=color,
            label=method,
        )
    axes[1].set(
        xscale="log",
        yscale="log",
        xlabel="Samples per replicate (log)",
        ylabel="Relative RMSE versus finite-q oracle, % (log)",
        title="t₄, ρ=0.5, q=0.999; 80 replicates",
    )
    axes[1].legend()
    axes[1].set_xticks([2000, 20000], labels=["2,000", "20,000"])
    fig.suptitle("Known-parameter copula audit — finite thresholds are not asymptotic limits", fontsize=12)
    fig.savefig(OUT / "audit.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    config = json.loads((ROOT / "config.json").read_text())
    grid = run_grid(config)
    raw, memory = run_mc(config, grid)
    summary = summarize(raw)
    rank_rows = []
    examples = {}
    for i, spec in enumerate(config["grid"]["models"]):
        model = Copula(0.5, spec["df"])
        x = sample_latent(
            model, config["rank_check"]["n"], np.random.default_rng(config["rank_check"]["seed"] + i)
        )
        examples[spec["name"]] = x
        rank_rows.append(
            {
                "model": spec["name"],
                "rho": 0.5,
                "df": spec["df"],
                "n": len(x),
                "seed": config["rank_check"]["seed"] + i,
                "population_tau": kendall_tau(model),
                "empirical_tau": float(kendalltau(x[:, 0], x[:, 1]).statistic),
            }
        )
    selected = [r for r in summary if r["model"] == "t4" and r["q"] == 0.999 and r["n"] == 20000]
    d = next(r for r in selected if r["method"] == "direct")
    c = next(r for r in selected if r["method"] == "conditional")
    g = next(r for r in grid if r["model"] == "gaussian" and r["q"] == 0.999 and r["rho"] == 0.5)
    t4 = next(r for r in grid if r["model"] == "t4" and r["q"] == 0.999 and r["rho"] == 0.5)
    checks = {
        "max_quadrature_disagreement": max(r["coordinate_disagreement"] for r in grid),
        "max_independence_error": max(
            abs(r["finite_lambda"] - (1 - r["q"])) for r in grid if r["model"] == "gaussian" and r["rho"] == 0
        ),
        "max_empirical_kendall_error": max(abs(r["empirical_tau"] - r["population_tau"]) for r in rank_rows),
        "min_t4_to_gaussian_joint_ratio": t4["joint_probability"] / g["joint_probability"],
        "max_conditional_to_direct_rmse_ratio": c["rmse"] / d["rmse"],
        "max_conditional_relative_rmse": c["relative_rmse"],
        "max_variance_bound_violation": max(r["variance_bound_violation"] for r in grid),
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
            for p in ["numpy", "scipy", "matplotlib", "nbformat", "pytest", "hypothesis", "ruff", "mypy"]
        },
        "threads": {p: os.getenv(p) for p in ["OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"]},
        "policy": config["hardware"],
    }
    write_csv("population.csv", grid)
    write_csv("raw.csv", raw)
    write_csv("summary.csv", summary)
    write_csv("memory.csv", memory)
    write_csv("rank_check.csv", rank_rows)
    np.savez_compressed(
        OUT / "latent_examples.npz", gaussian=examples["gaussian"], t4=examples["t4"], t30=examples["t30"]
    )
    results = {
        "checks": checks,
        "passed": passed,
        "grid_cases": len(grid),
        "timed_runs": len(raw),
        "gate_scenario": config["gate_scenario"],
        "selected": {"gaussian": g, "t4": t4, "direct": d, "conditional": c},
        "metadata": metadata,
    }
    (OUT / "results.json").write_text(json.dumps(results, indent=2, allow_nan=False) + "\n")
    plot_results(grid, summary)
    print(json.dumps({"checks": checks, "passed": passed}, indent=2))
    if not all(passed.values()):
        raise RuntimeError("Predeclared gate failed; raw evidence retained")


if __name__ == "__main__":
    main()
