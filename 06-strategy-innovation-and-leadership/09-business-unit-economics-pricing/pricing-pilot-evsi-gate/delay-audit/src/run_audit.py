"""Reproduce exact finite-horizon delay analysis, sensitivity, and diagnostics."""
from __future__ import annotations

import csv
import json
import random
import sys
from importlib import import_module
from pathlib import Path
from time import perf_counter

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from evsi_delay import Arm, analyze

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
sys.path.insert(0, str(ROOT.parent / "src"))
legacy_evsi = import_module("evsi")
Price, evaluate = legacy_evsi.Price, legacy_evsi.evaluate


def load_config() -> dict:
    return json.loads((ROOT / "config.json").read_text())


def main() -> None:
    cfg = load_config()
    OUT.mkdir(exist_ok=True)
    a0, b0 = cfg["prior"]["arm_a"], cfg["prior"]["arm_b"]
    a, b = Arm(**a0), Arm(**b0)
    n, horizon, cost = cfg["n_per_arm"], cfg["horizon_periods"], cfg["pilot_cost"]
    rows = [analyze(a, b, n, horizon, d, cost) for d in cfg["delay_periods"]]
    with (OUT / "delay_sensitivity.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    prior_rows = []
    for mult in cfg["prior_concentration_multipliers"]:
        aa, ab = Arm(a.alpha*mult, a.beta*mult, a.margin), Arm(b.alpha*mult, b.beta*mult, b.margin)
        prior_rows.append({"concentration_multiplier": mult, **analyze(aa, ab, n, horizon, 5, cost)})
    with (OUT / "prior_sensitivity.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(prior_rows[0])); w.writeheader(); w.writerows(prior_rows)

    benchmark_rows = []
    for benchmark_n in (5, 10, 20, 40):
        started = perf_counter()
        result = analyze(a, b, benchmark_n, horizon, 0, cost)
        benchmark_rows.append({"n_per_arm": benchmark_n, "outcome_pairs": (benchmark_n+1)**2,
                               "elapsed_seconds": perf_counter()-started,
                               "net_gain": result["net_gain"]})
    with (OUT / "benchmark.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(benchmark_rows[0])); w.writeheader(); w.writerows(benchmark_rows)

    # Negative ablation: re-use the pre-existing EVSI rule, which ignores the commercial delay.
    ablation_cost = 0.0  # isolate delay from the direct study cost
    ablation_delay = 10
    legacy = evaluate([Price("A", a.margin, a.alpha, a.beta), Price("B", b.margin, b.alpha, b.beta)], n, ablation_cost)
    ablation = {"baseline": "pricing-pilot-evsi-gate EVSI minus pilot cost; ignores foregone horizon",
                "comparison_cost": ablation_cost, "delay_periods": ablation_delay,
                "baseline_decision": legacy["decision"], "baseline_net_evsi": legacy["net_evsi"],
                "delay_aware_decision": analyze(a, b, n, horizon, ablation_delay, ablation_cost)["decision"],
                "delay_aware_net_gain": analyze(a, b, n, horizon, ablation_delay, ablation_cost)["net_gain"],
                "interpretation": "Negative ablation exposes a decision flip caused by omitting delay; no commercial claim."}
    (OUT / "ablation.json").write_text(json.dumps(ablation, indent=2)+"\n")

    # Independent simulation check: draw latent conversion rates then binomial outcomes.
    rng = random.Random(cfg["seed"])
    reps = cfg["monte_carlo_replications"]
    totals = []
    for _ in range(reps):
        pa, pb = rng.betavariate(a.alpha, a.beta), rng.betavariate(b.alpha, b.beta)
        xa = sum(rng.random() < pa for _ in range(n)); xb = sum(rng.random() < pb for _ in range(n))
        totals.append(max(a.margin*(a.alpha+xa)/(a.alpha+a.beta+n), b.margin*(b.alpha+xb)/(b.alpha+b.beta+n)))
    mc_mean = sum(totals)/reps
    exact = rows[0]["posterior_best_margin"]
    mc = {"replications": reps, "seed": cfg["seed"], "exact_expected_best_margin": exact,
          "monte_carlo_mean": mc_mean, "absolute_difference": abs(mc_mean-exact),
          "mc_standard_error": (sum((x-mc_mean)**2 for x in totals)/(reps-1)/reps)**0.5,
          "purpose": "implementation cross-check; simulation is not an empirical validation"}
    (OUT / "monte_carlo_check.json").write_text(json.dumps(mc, indent=2)+"\n")

    # High-concentration numerical audit for mass drift and tiny negative EVSI residuals.
    from evsi_delay import predictive
    numeric = []
    for mult in (1, 10, 100, 1000):
        mass = sum(predictive(k, n, a.alpha*mult, a.beta*mult) for k in range(n+1))
        result = analyze(Arm(a.alpha*mult, a.beta*mult, a.margin),
                         Arm(b.alpha*mult, b.beta*mult, b.margin), n, horizon, 0, 0)
        numeric.append({"concentration_multiplier": mult, "predictive_mass": mass,
                        "mass_error": mass-1, "raw_evsi": result["evsi"],
                        "negative_roundoff_flag": result["evsi_negative_roundoff"]})
    (OUT / "numerical_audit.json").write_text(json.dumps(numeric, indent=2)+"\n")

    ds = [r["delay"] for r in rows]
    plt.figure(figsize=(8, 4.8))
    plt.plot(ds, [r["net_gain"] for r in rows], marker="o", label="Piloto con demora − decisión inmediata")
    plt.axhline(0, color="black", lw=0.8)
    plt.xlabel("Demora (periodos del horizonte sintético)"); plt.ylabel("Ganancia neta esperada (unidades abstractas)")
    plt.title("El costo de oportunidad puede invertir la decisión EVSI"); plt.grid(alpha=.25); plt.legend(); plt.tight_layout()
    plt.savefig(OUT / "delay_frontier.png", dpi=160); plt.close()
    base_per_period = max(a.margin*a.alpha/(a.alpha+a.beta), b.margin*b.alpha/(b.alpha+b.beta))
    break_even = horizon-(horizon*base_per_period+cost)/exact if exact else None
    summary = {"synthetic": True, "config": cfg, "delay_scenarios": rows,
               "pilot_vs_launch_break_even_delay_periods": break_even,
               "posterior_best_margin_per_period": exact,
               "immediate_best_margin_per_period": base_per_period,
               "negative_ablation": ablation, "monte_carlo": mc, "numerical_audit": numeric}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    print(json.dumps({"scenario_count": len(rows), "mc_abs_difference": mc["absolute_difference"],
                      "ablation_decision_flip": ablation["baseline_decision"] != ablation["delay_aware_decision"],
                      "pilot_vs_launch_break_even_delay_periods": break_even}, indent=2))


if __name__ == "__main__":
    main()
