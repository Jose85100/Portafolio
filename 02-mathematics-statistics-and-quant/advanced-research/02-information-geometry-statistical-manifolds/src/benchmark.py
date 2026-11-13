"""Reproducible categorical geometry and matched-permutation audit."""

import csv
import json
import math
import platform
import time
import tracemalloc
from pathlib import Path
from collections.abc import Callable
import numpy as np
from src.geometry import fisher_rao, hellinger, local_fisher, geodesic
from src.reference import oracle_fr
from src.testing import permutation_test

OUT = Path("benchmarks")


def write_csv(name: str, rows: list[dict]) -> None:
    with (OUT / name).open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def distributions(k: int, scenario: str) -> tuple[np.ndarray, np.ndarray]:
    p = np.ones(k) / k
    if scenario in ("null_sparse", "shift_rare"):
        p = np.full(k, 0.1 / (k - 1))
        p[0] = 0.9
    q = p.copy()
    if scenario == "shift_dense":
        q[: k // 2] *= 1.4
        q[k // 2 :] *= 0.6
    elif scenario == "shift_rare":
        q[0] -= 0.04
        q[-1] += 0.04
    return p, q


def wilson(successes: int, n: int) -> tuple[float, float]:
    z = 1.959963984540054
    rate = successes / n
    mid = (rate + z * z / (2 * n)) / (1 + z * z / n)
    radius = z * math.sqrt(rate * (1 - rate) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (0.0 if successes == 0 else mid - radius, 1.0 if successes == n else mid + radius)


def plot(summary: list[dict], timings: list[dict]) -> None:
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(17, 5), layout="constrained")
    labels = ["FR perm.", "Hellinger perm.", "Pearson perm.", "Pearson asym."]
    methods = ["p_fr", "p_hellinger", "p_pearson", "p_pearson_asymptotic"]
    colors = ["#24658A", "#C17922", "#66783B", "#A94F78"]
    markers = ["o", "s", "^", "D"]
    for panel, scenario in enumerate(["null_sparse", "shift_rare"]):
        for i, method in enumerate(methods):
            row = next(
                r
                for r in summary
                if r["k"] == 32 and r["n"] == 100 and r["scenario"] == scenario and r["method"] == method
            )
            axes[panel].errorbar(
                i,
                row["rate"],
                yerr=[[row["rate"] - row["lower95"]], [row["upper95"] - row["rate"]]],
                fmt=markers[i],
                color=colors[i],
                capsize=4,
            )
        axes[panel].set_xticks(range(4), labels, rotation=25, ha="right")
        axes[panel].set_ylim(0, 1)
        axes[panel].set_ylabel("Rejection fraction (100 independent datasets)")
        axes[panel].set_title("Sparse null" if panel == 0 else "Rare-category shift")
        axes[panel].axhline(0.05, color="#444444", ls="--", lw=1)
    for method, color, marker in zip(
        ["fr", "hellinger", "local_fisher"], colors[:3], markers[:3], strict=True
    ):
        dims = sorted({r["k"] for r in timings})
        means = [
            np.median([r["seconds"] for r in timings if r["k"] == k and r["method"] == method]) * 1e6
            for k in dims
        ]
        axes[2].plot(dims, means, color=color, marker=marker, label=method)
    axes[2].set_xscale("log")
    axes[2].set_yscale("log")
    axes[2].set_xlabel("Number of categories (log)")
    axes[2].set_ylabel("Median function time, microseconds (log)")
    axes[2].set_title("Local timing; validation included")
    axes[2].legend()
    fig.suptitle("Categorical two-sample audit — K=32, n=m=100, 199 shared partitions")
    fig.text(
        0.01,
        -0.04,
        "Intervals: 95% Wilson across datasets, not simultaneous. FR and Hellinger are monotone-equivalent; no added detection power claimed.",
        fontsize=10,
    )
    fig.savefig(OUT / "audit.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    config = json.loads(Path("config.json").read_text())
    OUT.mkdir(exist_ok=True)
    rows = []
    allcounts = []
    truth = []
    idx = 0
    for k in config["categories"]:
        for n in config["sample_sizes"]:
            for scenario in config["scenarios"]:
                p, q = distributions(k, scenario)
                truth.append({"k": k, "n": n, "scenario": scenario, "p": p.tolist(), "q": q.tolist()})
                for rep in range(config["replicates"]):
                    seed = config["seed"] + idx * 2
                    rng = np.random.default_rng(seed)
                    sample_a, sample_b = rng.multinomial(n, p), rng.multinomial(n, q)
                    tracemalloc.start()
                    start = time.perf_counter()
                    test_result = permutation_test(
                        sample_a.astype(float), sample_b.astype(float), config["permutations"], seed + 1
                    )
                    seconds = time.perf_counter() - start
                    _, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    row = {
                        "id": idx,
                        "k": k,
                        "n": n,
                        "scenario": scenario,
                        "replicate": rep,
                        "data_seed": seed,
                        "permutation_seed": seed + 1,
                        "seconds": seconds,
                        "peak_traced_bytes": peak,
                        **test_result,
                    }
                    rows.append(row)
                    padded = np.zeros((2, max(config["categories"])), dtype=np.int64)
                    padded[:, :k] = np.stack([sample_a, sample_b])
                    allcounts.append(padded)
                    idx += 1
    write_csv("replicates.csv", rows)
    np.savez_compressed(OUT / "counts.npz", counts=np.stack(allcounts))
    (OUT / "distributions.json").write_text(json.dumps(truth, indent=2) + "\n")
    summary = []
    methods = ["p_fr", "p_hellinger", "p_pearson", "p_pearson_asymptotic"]
    for k in config["categories"]:
        for n in config["sample_sizes"]:
            for scenario in config["scenarios"]:
                subset = [r for r in rows if r["k"] == k and r["n"] == n and r["scenario"] == scenario]
                for method in methods:
                    successes = sum(r[method] <= config["alpha"] for r in subset)
                    lo, hi = wilson(successes, len(subset))
                    summary.append(
                        {
                            "k": k,
                            "n": n,
                            "scenario": scenario,
                            "method": method,
                            "replicates": len(subset),
                            "rejections": successes,
                            "rate": successes / len(subset),
                            "lower95": lo,
                            "upper95": hi,
                        }
                    )
    write_csv("summary.csv", summary)
    rng = np.random.default_rng(config["seed"])
    timings = []
    functions: dict[str, Callable] = {"fr": fisher_rao, "hellinger": hellinger, "local_fisher": local_fisher}
    for k in config["benchmark_dimensions"]:
        p = rng.dirichlet(np.ones(k))
        q = 0.99 * p + 0.01 * np.ones(k) / k
        for name, fn in functions.items():
            fn(p, q)  # separate warmup, input creation excluded
            for repeat in range(config["timing_repeats"]):
                start = time.perf_counter()
                value = fn(p, q)
                seconds = time.perf_counter() - start
                tracemalloc.start()
                fn(p, q)
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                timings.append(
                    {
                        "k": k,
                        "method": name,
                        "repeat": repeat,
                        "seconds": seconds,
                        "peak_traced_bytes": peak,
                        "value": value,
                    }
                )
    write_csv("timings.csv", timings)
    audits = []
    paths = []
    oracles = []
    for k in [2, 8, 32]:
        p = rng.dirichlet(np.ones(k))
        for step in [1e-12, 1e-6, 0.1, 1.0]:
            q = (1 - step) * p + step * np.ones(k) / k
            fr = fisher_rao(p, q)
            h = hellinger(p, q)
            oracle = oracle_fr(p, q)
            naive = float(2 * np.arccos(np.clip(np.sum(np.sqrt(p * q)), 0, 1)))
            oracles.append(
                {
                    "k": k,
                    "step": step,
                    "fr": fr,
                    "oracle": oracle,
                    "abs_error": abs(fr - oracle),
                    "naive_acos": naive,
                    "naive_error": abs(naive - oracle),
                }
            )
            audits.append({"identity_error": abs(fr - 4 * np.arcsin(h / math.sqrt(2)))})
            for t in np.linspace(0, 1, 11):
                g = geodesic(p, q, float(t))
                paths.append(
                    {
                        "k": k,
                        "step": step,
                        "t": float(t),
                        "distance_from_start": fisher_rao(p, g),
                        "expected": float(t) * fr,
                        "error": abs(fisher_rao(p, g) - t * fr),
                    }
                )
    write_csv("oracle.csv", oracles)
    write_csv("geodesics.csv", paths)
    a = np.array([0.99, 0.01])
    b = np.array([0.5, 0.5])
    small = a + 1e-6 * (b - a)
    counter = {
        "p": a.tolist(),
        "q": b.tolist(),
        "fr": fisher_rao(a, b),
        "hellinger": hellinger(a, b),
        "local_at_p": local_fisher(a, b),
        "local_at_q": local_fisher(b, a),
        "naive_acos_nearby": next(r for r in oracles if r["k"] == 2 and r["step"] == 1e-12),
    }
    checks = {
        "max_pvalue_difference": max(abs(r["p_fr"] - r["p_hellinger"]) for r in rows),
        "max_oracle_error": max(r["abs_error"] for r in oracles),
        "max_geodesic_error": max(r["error"] for r in paths),
        "max_identity_error": max(r["identity_error"] for r in audits),
        "max_local_smallstep_relative_error": abs(local_fisher(a, small) / fisher_rao(a, small) - 1),
        "min_local_asymmetry": local_fisher(a, b) - local_fisher(b, a),
        "min_local_exceeds_pi": local_fisher(a, b) - math.pi,
    }
    passed = {
        key: bool(value <= config["checks"][key] if key.startswith("max") else value >= config["checks"][key])
        for key, value in checks.items()
    }
    result = {
        "checks": checks,
        "passed": passed,
        "counterexample": counter,
        "hardware": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "design": {
            "datasets": len(rows),
            "test_results": len(rows) * len(methods),
            "random_partitions": len(rows) * config["permutations"],
            "timing_rows": len(timings),
            "oracle_rows": len(oracles),
            "geodesic_rows": len(paths),
        },
    }
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    plot(summary, timings)
    print(json.dumps(result, indent=2))
    if not all(passed.values()):
        raise AssertionError("predefined audit gate failed")


if __name__ == "__main__":
    main()
