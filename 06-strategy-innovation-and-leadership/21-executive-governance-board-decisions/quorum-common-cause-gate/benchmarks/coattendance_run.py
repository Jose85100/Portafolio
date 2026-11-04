"""Reproducible synthetic menu experiment, exact coverage audit and drift ablation."""
import json
from math import comb
from pathlib import Path
import platform
import statistics
import time
import tracemalloc

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.stats import beta

from src.coattendance_gate import (
    PlanCount, binomial_lower_oracle, clopper_pearson_lower,
    exact_lower_coverage, hoeffding_lower, select_plan, simultaneous_bounds,
)


def save_csv(path: Path, rows: list[dict]) -> None:
    import csv
    if not rows:
        raise ValueError(f"no rows to write: {path}")
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_config(root: Path) -> tuple[dict, list[PlanCount]]:
    config = json.loads((root / "config_coattendance.json").read_text())
    plans = [PlanCount(**item) for item in config["fixed_menu"]]
    return config, plans


def exact_oracle_grid() -> list[dict]:
    rows = []
    alpha = .05 / 3
    trials_grid = (10, 20, 40, 60, 80, 100, 120, 140, 160, 180)
    probabilities = np.linspace(.05, .95, 23)
    for n in trials_grid:
        for p in probabilities:
            x = min(n, max(1, round(n * float(p))))
            candidate = clopper_pearson_lower(x, n, alpha)
            oracle = binomial_lower_oracle(x, n, alpha)
            tail = sum(comb(n, k) * candidate**k * (1-candidate)**(n-k)
                       for k in range(x, n + 1))
            rows.append({"trials": n, "probability_grid": float(p), "successes": x,
                         "cp_beta_quantile": candidate, "independent_bisection": oracle,
                         "oracle_abs_error": abs(candidate-oracle), "tail_at_candidate": tail,
                         "tail_target": alpha})
    assert len(rows) == 230
    return rows


def exact_coverage_grid() -> list[dict]:
    rows = []
    for n in (20, 50, 100, 200, 500, 1000):
        for p in np.linspace(.05, .95, 101):
            for method in ("clopper_pearson", "hoeffding"):
                alpha = .05 / 3
                coverage = exact_lower_coverage(n, float(p), alpha, method)
                rows.append({"trials": n, "true_probability": float(p), "method": method,
                             "per_plan_alpha": alpha, "nominal_marginal_coverage": 1-alpha,
                             "exact_coverage": coverage})
    # Two methods on each n/p cell; 606 cells, 1,212 method rows.
    assert len(rows) == 1212
    return rows


def mc_experiment(config: dict) -> tuple[list[dict], dict]:
    experiment = config["experiments"]
    n = experiment["sessions_per_run"]
    break_at = experiment["drift_break"]
    per_plan_alpha = config["family_alpha"] / len(config["fixed_menu"])
    rows = []
    for seed in experiment["monte_carlo_seeds"]:
        rng = np.random.default_rng(seed)
        for scenario in ("stationary", "drift"):
            reps = experiment["monte_carlo_rows"] // (len(experiment["monte_carlo_seeds"])*2)
            for rep in range(reps):
                if scenario == "stationary":
                    p = experiment["stationary_probability"]
                    x = int(rng.binomial(n, p))
                    reference = p
                else:
                    p0, p1 = experiment["drift_pre_probability"], experiment["drift_post_probability"]
                    x = int(rng.binomial(break_at, p0) + rng.binomial(n-break_at, p1))
                    # Score validity against current post-break rate, not pooled mean.
                    reference = p1
                lower_cp = clopper_pearson_lower(x, n, per_plan_alpha)
                lower_h = hoeffding_lower(x, n, per_plan_alpha)
                rows.append({"seed": seed, "scenario": scenario, "replicate": rep,
                             "successes": x, "trials": n, "current_reference_probability": reference,
                             "cp_lower": lower_cp, "hoeffding_lower": lower_h,
                             "cp_covers_current": int(lower_cp <= reference),
                             "hoeffding_covers_current": int(lower_h <= reference)})
    assert len(rows) == experiment["monte_carlo_rows"]
    summary = {}
    for scenario in ("stationary", "drift"):
        subset = [row for row in rows if row["scenario"] == scenario]
        record = {"runs": len(subset)}
        for method, key in (("clopper_pearson", "cp_covers_current"),
                             ("hoeffding", "hoeffding_covers_current")):
            successes = sum(row[key] for row in subset)
            # Pointwise exact binomial interval for Monte Carlo coverage uncertainty.
            record[method] = {"covered": successes, "coverage": successes/len(subset),
                              "mc_95_interval": [0.0 if successes == 0 else float(beta.ppf(.025, successes, len(subset)-successes+1)),
                                                 1.0 if successes == len(subset) else float(beta.ppf(.975, successes+1, len(subset)-successes))]}
        summary[scenario] = record
    return rows, summary


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    config, plans = load_config(root)
    target, delta = config["target"], config["family_alpha"]
    cp_rows = simultaneous_bounds(plans, delta, "clopper_pearson")
    h_rows = simultaneous_bounds(plans, delta, "hoeffding")
    for cp, h in zip(cp_rows, h_rows):
        cp["hoeffding_lower"] = h["lower"]
        cp["target"] = target
        cp["cp_pass"] = cp["lower"] >= target
        cp["hoeffding_pass"] = h["lower"] >= target
    selected_cp = select_plan(plans, target, delta, "clopper_pearson")
    selected_h = select_plan(plans, target, delta, "hoeffding")
    (root / "results").mkdir(exist_ok=True)
    save_csv(root/"results/coattendance_synthetic_counts.csv", [
        {"plan": p.name, "abstract_cost": p.cost, "quorum_successes": p.successes,
         "synthetic_trials": p.trials, "empirical_data": False} for p in plans])
    save_csv(root/"results/coattendance_decision.csv", cp_rows)
    oracle = exact_oracle_grid()
    save_csv(root/"results/coattendance_oracle_230.csv", oracle)
    coverage = exact_coverage_grid()
    save_csv(root/"results/coattendance_exact_coverage.csv", coverage)
    mc_rows, mc_summary = mc_experiment(config)
    save_csv(root/"results/coattendance_mc_trials.csv", mc_rows)

    # Drift counterexample compares a fixed stationary threshold to the current post-break rate.
    drift_summary = mc_summary["drift"]
    stationary_summary = mc_summary["stationary"]
    timings = []
    for method in ("clopper_pearson", "hoeffding"):
        f = clopper_pearson_lower if method == "clopper_pearson" else hoeffding_lower
        for n in (200, 1000, 5000):
            for repetitions in (1000,):
                for _ in range(5):
                    tracemalloc.start()
                    start = time.perf_counter()
                    for _ in range(repetitions):
                        f(round(.65*n), n, delta/len(plans))
                    seconds = time.perf_counter()-start
                    peak = tracemalloc.get_traced_memory()[1]
                    tracemalloc.stop()
                    timings.append({"method": method, "trials": n, "repetitions": repetitions,
                                    "seconds": seconds, "python_peak_bytes": peak})
    save_csv(root/"results/coattendance_runtime.csv", timings)
    summary = {
        "selected_cp": selected_cp, "selected_hoeffding": selected_h, "target": target,
        "family_alpha": delta, "menu_size": len(plans), "bonferroni_alpha_each": delta/len(plans),
        "decision_rows": cp_rows, "oracle_comparisons": len(oracle),
        "oracle_max_abs_error": max(r["oracle_abs_error"] for r in oracle),
        "oracle_max_tail_residual": max(abs(r["tail_at_candidate"]-r["tail_target"]) for r in oracle),
        "exact_coverage_cells": len(coverage)//2, "exact_coverage_method_rows": len(coverage), "minimum_exact_coverage_by_method": {
            method: min(row["exact_coverage"] for row in coverage if row["method"] == method)
            for method in ("clopper_pearson", "hoeffding")},
        "monte_carlo_rows": len(mc_rows), "monte_carlo": mc_summary,
        "drift_counterexample": {"stationary_coverage": stationary_summary,
                                 "against_current_post_break_probability": drift_summary},
        "runtime_median_seconds_per_1000_calls": {method: {
            str(n): statistics.median(r["seconds"] for r in timings if r["method"] == method and r["trials"] == n)
            for n in (200, 1000, 5000)} for method in ("clopper_pearson", "hoeffding")},
        "python": platform.python_version(), "platform": platform.platform(),
        "processor": platform.processor(), "numpy": np.__version__, "scipy": scipy.__version__,
        "memory_scope": "Python tracemalloc allocation; excludes native SciPy and RSS",
        "evidence": "All counts, grids and simulation are designed synthetic; no observed meetings, no empirical validation",
        "seed": config["seed"],
    }
    (root/"results/coattendance_summary.json").write_text(json.dumps(summary, indent=2)+"\n")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    x = np.arange(len(plans))
    axes[0].bar(x-.18, [row["lower"] for row in cp_rows], .36, label="Clopper–Pearson + Bonferroni")
    axes[0].bar(x+.18, [row["hoeffding_lower"] for row in cp_rows], .36, label="Hoeffding + same Bonferroni")
    axes[0].axhline(target, color="black", linestyle=":", label=f"Target {target:.2f}")
    axes[0].set(xticks=x, xticklabels=[f"{p.name} · cost {p.cost:g}" for p in plans],
                ylim=(.35, .75), ylabel="Simultaneous lower confidence bound",
                title="Same counts, menu, error budget")
    axes[0].legend(fontsize=8)
    for i, scenario in enumerate(("stationary", "drift")):
        subset = [r for r in mc_rows if r["scenario"] == scenario]
        n = len(subset)
        for j, (method, key, color) in enumerate((("CP", "cp_covers_current", "#2a6f97"),
                                                   ("Hoeffding", "hoeffding_covers_current", "#e07a1f"))):
            successes = sum(r[key] for r in subset)
            lower = 0 if successes == 0 else beta.ppf(.025, successes, n-successes+1)
            upper = 1 if successes == n else beta.ppf(.975, successes+1, n-successes)
            xpos = i + (-.18 if j == 0 else .18)
            axes[1].bar(xpos, successes/n, width=.34, color=color, label=method if i == 0 else None)
            axes[1].errorbar([xpos], [successes/n],
                             yerr=[[successes/n-lower], [upper-successes/n]], fmt="none",
                             ecolor="black", capsize=3)
    axes[1].axhline(1-delta/len(plans), color="black", linestyle=":",
                    label=f"Nominal marginal coverage {1-delta/len(plans):.2%}")
    axes[1].set(xticks=[0, 1], xticklabels=["Stationary: p=0.6", "Drift: 0.7→0.5 (current=0.5)"],
                ylabel="Monte Carlo coverage against reference probability",
                title="Drift; zoomed axis 0.20–1.00", ylim=(.2, 1.01))
    axes[0].set_title("Same counts/menu/budget; zoom 0.35–0.75")
    axes[1].legend(fontsize=8)
    for axis in axes:
        axis.grid(axis="y", alpha=.2)
    fig.suptitle("Fixed-menu synthetic audit · not observed governance data")
    fig.savefig(root/"results/coattendance_gate.png", dpi=160)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
