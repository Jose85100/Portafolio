"""Reduction order audit: Decimal100, serial dynamic and offline scaled NumPy."""

import csv
import json
import math
import platform
import time
import tracemalloc
from decimal import Decimal, localcontext
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from src.dynamic import DynamicMoments


def summary(values: list[float]) -> DynamicMoments:
    state = DynamicMoments()
    for value in values:
        state = state.push(value)
    return state


def oracle(values: list[float], ddof: int) -> float:
    with localcontext() as ctx:
        ctx.prec = 100
        xs = [Decimal(x) for x in values]
        mean = sum(xs) / len(xs)
        return float((sum((x - mean) ** 2 for x in xs) / (len(xs) - ddof)).sqrt())


def reduce_states(states: list[DynamicMoments], tree: bool) -> DynamicMoments:
    if not states:
        return DynamicMoments()
    if tree:
        while len(states) > 1:
            states = [states[i].merge(states[i + 1]) for i in range(0, len(states), 2)]
        return states[0]
    result = DynamicMoments()
    for state in states:
        result = result.merge(state)
    return result


def main() -> None:
    config = json.loads(Path("config_merge.json").read_text())
    rows = []
    for seed in config["seeds"]:
        rng = np.random.default_rng(seed)
        for n in config["sizes"]:
            for e in config["exponents"]:
                xs = [
                    math.ldexp(float(x), e) for x in np.clip(rng.normal(size=n), -2, 2)
                ]
                scale = max(math.frexp(x)[1] for x in xs if x)
                for chunks in config["chunks"]:
                    parts = [xs[i : i + n // chunks] for i in range(0, n, n // chunks)]
                    states = [summary(part) for part in parts]
                    for ddof in config["ddof"]:
                        expected = oracle(xs, ddof)

                        def serial():
                            return summary(xs).result(ddof).std

                        def left():
                            return reduce_states(states[:], False).result(ddof).std

                        def tree():
                            return reduce_states(states[:], True).result(ddof).std

                        def tree_full():
                            fresh = [summary(part) for part in parts]
                            return reduce_states(fresh, True).result(ddof).std

                        def numpy_scaled():
                            return math.ldexp(
                                float(
                                    np.std(
                                        [math.ldexp(x, -scale) for x in xs], ddof=ddof
                                    )
                                ),
                                scale,
                            )

                        for name, fn in [
                            ("serial_dynamic", serial),
                            ("merge_left", left),
                            ("merge_tree", tree),
                            ("merge_tree_full", tree_full),
                            ("numpy_scaled", numpy_scaled),
                        ]:
                            times = []
                            for _ in range(config["repeats"]):
                                start = time.perf_counter_ns()
                                answer = fn()
                                times.append(time.perf_counter_ns() - start)
                            tracemalloc.start()
                            fn()
                            _, peak = tracemalloc.get_traced_memory()
                            tracemalloc.stop()
                            error = abs(answer - expected)
                            rows.append(
                                dict(
                                    seed=seed,
                                    n=n,
                                    exponent=e,
                                    chunks=chunks,
                                    ddof=ddof,
                                    method=name,
                                    sd=answer,
                                    oracle_sd=expected,
                                    relative_error=error / expected,
                                    absolute_error=error,
                                    gate=error
                                    <= max(4 * math.ulp(expected), 1e-12 * expected),
                                    median_ns=float(np.median(times)),
                                    peak_python_bytes=peak,
                                )
                            )
    with Path("results/merge_raw.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    merged = [r for r in rows if r["method"].startswith("merge")]
    output = {
        "scenario_count": len(rows) // 5,
        "rows": len(rows),
        "merged_comparisons": len(merged),
        "gate": all(r["gate"] for r in merged),
        "max_relative_error": max(r["relative_error"] for r in merged),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "hardware": platform.processor(),
        "timing_scope": "merge_left/tree exclude precomputed chunk summary; merge_tree_full/serial/NumPy include input scan; no parallel speedup claim; 5 repeats; imports/install excluded; tracemalloc separate Python heap not RSS",
        "median_ns": {
            m: float(np.median([r["median_ns"] for r in rows if r["method"] == m]))
            for m in [
                "serial_dynamic",
                "merge_left",
                "merge_tree",
                "merge_tree_full",
                "numpy_scaled",
            ]
        },
    }
    Path("results/merge_summary.json").write_text(json.dumps(output, indent=2) + "\n")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for method, marker in [
        ("merge_left", "o"),
        ("merge_tree", "x"),
        ("numpy_scaled", "+"),
    ]:
        sample = [r for r in rows if r["method"] == method]
        axes[0].scatter(
            [r["n"] for r in sample],
            [max(r["relative_error"], 1e-18) for r in sample],
            marker=marker,
            label=method,
            alpha=0.5,
        )
    axes[0].set_yscale("log")
    axes[0].set_xlabel("Observations (count)")
    axes[0].set_ylabel("Relative SD error vs Decimal100")
    axes[0].legend()
    axes[0].set_title("Seeds, scales, ddof and chunk counts varied")
    for method, marker in [("merge_left", "o"), ("merge_tree", "x")]:
        sample = [r for r in rows if r["method"] == method]
        axes[1].scatter(
            [r["chunks"] for r in sample],
            [r["median_ns"] / 1000 for r in sample],
            marker=marker,
            label=method,
            alpha=0.4,
        )
    axes[1].set_xlabel("Precomputed chunks (count)")
    axes[1].set_ylabel("Merge-only time (microseconds)")
    axes[1].legend()
    axes[1].set_title("No parallel execution or speedup claimed")
    fig.suptitle(
        "Synthetic binary64; zero error drawn at 1e-18 for log axis", fontsize=10
    )
    fig.tight_layout()
    fig.savefig("results/merge_audit.png", dpi=150)
    plt.close(fig)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
