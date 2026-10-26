"""Controlled finite-factor experiment and explicit high-correlation failure check."""

import csv
import hashlib
import json
import math
import platform
import sys
import time
import tracemalloc
from pathlib import Path

import numpy as np
import scipy
from scipy.special import ndtri

from src.base import PATH, independent_pmf, tail
from src.factor import common_factor_pmf, stability_passed
from src.plotting import render

ROOT = Path(__file__).resolve().parents[1]


def write_csv(path, rows):
    with path.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run() -> None:
    cfg = json.loads((ROOT / "benchmarks/config.json").read_text())
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    cases = {"granular": [3] * cfg["granular_count"], "concentrated": [100] + [10] * 20}
    rows = []
    summary = []
    trials = []
    pmf_rows = []
    start = time.perf_counter()
    tracemalloc.start()
    for name, weights in cases.items():
        ps = [cfg["pd"]] * len(weights)
        baseline = tail(independent_pmf(weights, ps), cfg["confidence"])
        for regime, rho in [("base", cfg["rho"]), ("stress", cfg["stress_rho"])]:
            reference = common_factor_pmf(weights, ps, rho, cfg["reference_order"])
            ref = tail(reference, cfg["confidence"])
            previous = None
            for order in cfg["orders"]:
                t = time.perf_counter()
                pmf = common_factor_pmf(weights, ps, rho, order)
                seconds = time.perf_counter() - t
                estimate = tail(pmf, cfg["confidence"])
                l1 = sum(abs(p - q) for p, q in zip(pmf, reference))
                stable = previous is not None and stability_passed(
                    previous,
                    pmf,
                    cfg["confidence"],
                    cfg["cdf_tolerance"],
                    cfg["es_tolerance"],
                )
                rows.append(
                    {
                        "case": name,
                        "regime": regime,
                        "rho": rho,
                        "nodes": order,
                        "var": estimate.var,
                        "es": estimate.es,
                        "es_error_vs_reference": estimate.es - ref.es,
                        "l1_vs_reference": l1,
                        "stable_vs_previous": stable,
                        "seconds": seconds,
                        "mass_error": abs(math.fsum(pmf) - 1),
                        "mean_error": abs(
                            sum(i * p for i, p in enumerate(pmf))
                            - sum(w * p for w, p in zip(weights, ps))
                        ),
                    }
                )
                previous = pmf
            summary.append(
                {
                    "case": name,
                    "regime": regime,
                    "rho": rho,
                    "independent_var": baseline.var,
                    "independent_es": baseline.es,
                    "factor_var": ref.var,
                    "factor_es": ref.es,
                    "relative_es_increase": ref.es / baseline.es - 1,
                    "last_stability_passed": rows[-1]["stable_vs_previous"],
                    "last_es_difference_vs_reference": rows[-1][
                        "es_error_vs_reference"
                    ],
                }
            )
            if regime == "base":
                for value, mass in enumerate(reference):
                    pmf_rows.append({"case": name, "loss": value, "probability": mass})
                for seed in range(cfg["mc_seeds"]):
                    rng = np.random.default_rng(seed)
                    z = rng.normal(size=(cfg["mc_draws"], 1))
                    eps = rng.normal(size=(cfg["mc_draws"], len(weights)))
                    latent = math.sqrt(rho) * z + math.sqrt(1 - rho) * eps
                    losses = (latent < ndtri(cfg["pd"])) @ np.array(weights)
                    empirical = (
                        np.bincount(losses, minlength=sum(weights) + 1)
                        / cfg["mc_draws"]
                    )
                    mc = tail(empirical.tolist(), cfg["confidence"])
                    trials.append(
                        {
                            "case": name,
                            "seed": seed,
                            "draws": cfg["mc_draws"],
                            "var": mc.var,
                            "es": mc.es,
                            "es_error_vs_reference": mc.es - ref.es,
                        }
                    )
    seconds = time.perf_counter() - start
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    write_csv(out / "convergence.csv", rows)
    write_csv(out / "summary.csv", summary)
    write_csv(out / "trials.csv", trials)
    write_csv(out / "pmf.csv", pmf_rows)
    oracle = common_factor_pmf([1, 1], [0.5, 0.5], 0.5, 64)
    both = 0.25 + math.asin(0.5) / (2 * math.pi)
    error = max(abs(a - b) for a, b in zip(oracle, [both, 1 - 2 * both, both]))
    granular = next(
        r for r in summary if r["case"] == "granular" and r["regime"] == "base"
    )
    meta = {
        "config": cfg,
        "seconds": seconds,
        "peak_tracemalloc_bytes": peak,
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "logical_cpus": __import__("os").cpu_count(),
        "analytic_orthant_max_error": error,
        "hypothesis_passed": granular["relative_es_increase"] >= 0.5
        and granular["last_stability_passed"]
        and error <= 1e-12,
        "reference_warning": "256-node GH is numerical reference, not truth or certified bound",
        "source_kernel": "sibling discrete-credit-tail-audit/src/loss.py unchanged",
        "source_kernel_sha256": hashlib.sha256(PATH.read_bytes()).hexdigest(),
    }
    (out / "metrics.json").write_text(json.dumps(meta, indent=2))
    render(ROOT)
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    run()
