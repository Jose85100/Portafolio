"""Held-out drift benchmark: calibration, evaluation and misspecification kept separate."""

import json
import math
import platform
import time
import tracemalloc
from pathlib import Path
import numpy as np
import mpmath as mp
from src.drift import calibrate, scores, normal_fr
from src.benchmark import write_csv, wilson

METHODS = ["fr", "ks", "w1"]


def draw(rng: np.random.Generator, n: int, scenario: str, c: dict) -> np.ndarray:
    if scenario == "matched_mixture":
        loc = c["mixture_location"]
        return rng.choice([-loc, loc], size=n) + rng.normal(scale=math.sqrt(1 - loc * loc), size=n)
    if scenario == "correlated_null":
        # Strictly stationary N(0,1) marginals, but not exchangeable with IID calibration windows.
        phi = c["ar1"]
        x = rng.normal(size=n)
        for t in range(1, n):
            x[t] = phi * x[t - 1] + math.sqrt(1 - phi * phi) * x[t]
        return x
    x = rng.normal(size=n)
    if scenario == "mean_shift":
        x += c["mean_shift"]
    if scenario == "scale_shift":
        x *= c["scale_shift"]
    return x


def plot(rows: list[dict]) -> None:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), layout="constrained")
    colors = {"fr": "#24658A", "ks": "#C17922", "w1": "#66783B"}
    markers = {"fr": "o", "ks": "s", "w1": "^"}
    scenarios = ["null", "mean_shift", "scale_shift", "matched_mixture", "correlated_null"]
    for ax, n in zip(axes, [32, 128], strict=True):
        for offset, method in zip([-0.16, 0, 0.16], METHODS, strict=True):
            subset = [
                next(r for r in rows if r["n"] == n and r["scenario"] == s and r["method"] == method)
                for s in scenarios
            ]
            values = np.array([r["rate"] for r in subset])
            lower = np.array([r["lower95"] for r in subset])
            upper = np.array([r["upper95"] for r in subset])
            ax.errorbar(
                np.arange(5) + offset,
                values,
                yerr=[values - lower, upper - values],
                fmt=markers[method],
                color=colors[method],
                capsize=3,
                label=method,
            )
        ax.axhline(0.05, color="#444444", ls="--", lw=1)
        ax.set_xticks(
            range(5),
            [
                "IID null",
                "Mean +0.8",
                "Scale x1.6",
                "Same moments,\nnew shape",
                "AR(1) null\n(calibration violated)",
            ],
        )
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("Alarm fraction; 95% Wilson across 300 datasets")
        ax.set_title(f"Fixed reference, n={n}; 399 separate calibration windows")
        ax.legend()
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Continuous drift detection — calibrated FR projection versus KS and Wasserstein-1")
    fig.savefig("benchmarks/drift.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    c = json.loads(Path("experiments/drift.json").read_text())
    summary = []
    calrows = []
    saved = {}
    thresholds = []
    for n in c["sizes"]:
        seed = c["seed"] + n
        rng = np.random.default_rng(seed)
        reference = rng.normal(size=n)
        windows = rng.normal(size=(c["calibration_windows"], n))
        detector = calibrate(reference, windows, c["alpha"], c["calibration_delta"])
        saved[f"reference_{n}"] = reference
        saved[f"calibration_preview_{n}"] = windows[:8]
        for i, row in enumerate(windows):
            values = scores(reference, row)
            calrows.append(
                {
                    "n": n,
                    "id": i,
                    "calibration_seed": seed,
                    **{m: float(values[j]) for j, m in enumerate(METHODS)},
                }
            )
        thresholds.append({"n": n, **{m: float(detector.thresholds[j]) for j, m in enumerate(METHODS)}})
        raw = []
        for si, scenario in enumerate(c["scenarios"]):
            for rep in range(c["evaluation_replicates"]):
                eval_seed = c["seed"] + 100000 + n * 10000 + si * 1000 + rep
                current = draw(np.random.default_rng(eval_seed), n, scenario, c)
                start = time.perf_counter()
                values, alarms = detector.predict(current)
                seconds = time.perf_counter() - start
                row = {
                    "n": n,
                    "scenario": scenario,
                    "replicate": rep,
                    "seed": eval_seed,
                    "seconds_three_methods": seconds,
                }
                row.update({m: float(values[j]) for j, m in enumerate(METHODS)})
                row.update({m + "_alarm": int(alarms[j]) for j, m in enumerate(METHODS)})
                raw.append(row)
                if rep < 3:
                    saved[f"{n}_{scenario}_{rep}"] = current
            for j, m in enumerate(METHODS):
                subset = [r for r in raw if r["scenario"] == scenario]
                count = sum(r[m + "_alarm"] for r in subset)
                lo, hi = wilson(count, len(subset))
                summary.append(
                    {
                        "n": n,
                        "scenario": scenario,
                        "method": m,
                        "datasets": len(subset),
                        "alarms": count,
                        "rate": count / len(subset),
                        "lower95": lo,
                        "upper95": hi,
                    }
                )
        write_csv(f"drift-raw-{n}.csv", raw)
    write_csv("drift-calibration.csv", calrows)
    write_csv("drift-summary.csv", summary)
    write_csv("drift-thresholds.csv", thresholds)
    Path("data").mkdir(exist_ok=True)
    np.savez_compressed("data/drift-examples.npz", **saved)
    oracle: list[dict[str, float]] = []
    with mp.workdps(80):
        for mu1, s, u, v in [
            (0.0, 1.0, 1e-12, 1.0),
            (0.0, 1.0, 0.8, 1.0),
            (0.0, 1.0, 0.0, 1.6),
            (2.0, 0.1, -3.0, 4.0),
        ]:
            z = ((mp.mpf(mu1) - u) ** 2 + 2 * (mp.mpf(s) - v) ** 2) / (4 * mp.mpf(s) * v)
            ref = float(mp.sqrt(2) * mp.acosh(1 + z))
            value = normal_fr(mu1, s, u, v)
            oracle.append(
                {
                    "mu": mu1,
                    "sigma": s,
                    "other_mu": u,
                    "other_sigma": v,
                    "oracle": ref,
                    "observed": value,
                    "error": abs(value - ref),
                }
            )
    write_csv("drift-oracle.csv", oracle)
    resources = []
    for n in c["sizes"]:
        a = saved[f"reference_{n}"]
        x = saved[f"{n}_mean_shift_0"]
        tracemalloc.start()
        scores(a, x)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        resources.append({"n": n, "peak_traced_bytes_three_scores": peak})
    rates = {(r["n"], r["scenario"], r["method"]): r["rate"] for r in summary}
    checks = {
        "oracle_error": max(r["error"] for r in oracle),
        "mean_power_n128": rates[(128, "mean_shift", "fr")],
        "scale_power_n128": rates[(128, "scale_shift", "fr")],
    }
    passed = {
        "oracle_error": checks["oracle_error"] <= c["checks"]["oracle_error"],
        "mean_power_n128": checks["mean_power_n128"] >= c["checks"]["mean_power_n128_min"],
        "scale_power_n128": checks["scale_power_n128"] >= c["checks"]["scale_power_n128_min"],
    }
    result = {
        "checks": checks,
        "passed": passed,
        "thresholds": thresholds,
        "resources": resources,
        "hardware": {"platform": platform.platform(), "python": platform.python_version()},
        "scope": "One alarm per independent batch. No sequential-horizon error guarantee. AR1 null intentionally violates calibration.",
        "calibration_score_rows": len(calrows),
        "evaluation_datasets": 2 * 5 * c["evaluation_replicates"],
        "mixture_population": {
            "mean": 0,
            "variance": 1,
            "gaussian_projection_fr": 0,
            "note": "Different shape; FR here compares projected normals, not true mixture laws.",
        },
    }
    Path("benchmarks/drift-results.json").write_text(json.dumps(result, indent=2) + "\n")
    plot(summary)
    print(json.dumps(result, indent=2))
    if not all(passed.values()):
        raise AssertionError("Drift hypothesis failed; preserve results and investigate")


if __name__ == "__main__":
    main()
