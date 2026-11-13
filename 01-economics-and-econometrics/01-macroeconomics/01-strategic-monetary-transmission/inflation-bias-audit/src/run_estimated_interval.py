"""Fixed-design simulation: calibration vs temporal and tail misspecification."""

from __future__ import annotations
import gzip
from typing import Any
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
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .variance_interval import gaussian_variance_interval, wilson_interval
from .ambiguity import robust_weight, regret, worst_regret
from .delegation import optimal_weight


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    c = json.loads((root / "estimated-interval-config.json").read_text())
    rows: list[dict[str, Any]] = []
    shocks: list[dict[str, Any]] = []
    for seed in c["seeds"]:
        rng = np.random.default_rng(seed)
        for n in c["n"]:
            for v in c["historical_variance"]:
                for regime in c["regimes"]:
                    for rep in range(c["repetitions_per_seed_cell"]):
                        x = (
                            rng.standard_t(5, n) * math.sqrt(v * 3 / 5)
                            if regime == "iid_student_t5"
                            else rng.normal(0, math.sqrt(v), n)
                        )
                        truth = v * 4 if regime == "variance_break_x4" else v
                        sample_id = len(rows)
                        shocks.extend(
                            dict(sample_id=sample_id, time=i + 1, shock=float(value))
                            for i, value in enumerate(x)
                        )
                        ci = gaussian_variance_interval(x.tolist(), c["confidence"])
                        if ci is None:
                            rows.append(
                                dict(
                                    sample_id=sample_id,
                                    seed=seed,
                                    n=n,
                                    historical_variance=v,
                                    future_variance=truth,
                                    regime=regime,
                                    repetition=rep,
                                    abstain=1,
                                    covered=0,
                                    low=None,
                                    high=None,
                                    sample_variance=None,
                                    plugin_q=None,
                                    robust_q=None,
                                    plugin_regret=None,
                                    robust_regret=None,
                                    robust_bound=None,
                                    guarantee_violation=None,
                                )
                            )
                            continue
                        plug = optimal_weight(
                            1, 1, 1, math.sqrt(min(ci.sample_variance, 16))
                        )
                        robust = robust_weight(1, 1, 1, ci.low, ci.high)
                        rr = regret(robust, 1, 1, 1, truth)
                        bound = worst_regret(robust, 1, 1, 1, ci.low, ci.high)
                        covered = int(ci.low <= truth <= ci.high)
                        rows.append(
                            dict(
                                sample_id=sample_id,
                                seed=seed,
                                n=n,
                                historical_variance=v,
                                future_variance=truth,
                                regime=regime,
                                repetition=rep,
                                abstain=0,
                                covered=covered,
                                low=ci.low,
                                high=ci.high,
                                sample_variance=ci.sample_variance,
                                plugin_q=plug,
                                robust_q=robust,
                                plugin_regret=regret(plug, 1, 1, 1, truth),
                                robust_regret=rr,
                                robust_bound=bound,
                                guarantee_violation=int(rr > bound + 1e-10),
                            )
                        )
    out = root / "results"
    for name, data in [
        ("estimated-interval.csv", rows),
        ("estimated-shocks.csv", shocks),
    ]:
        with (out / name).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)
    raw_path = out / "estimated-shocks.csv"
    (out / "estimated-shocks.csv.gz").write_bytes(
        gzip.compress(raw_path.read_bytes(), mtime=0)
    )
    raw_path.unlink()
    aggregates = []
    for regime in c["regimes"]:
        for n in c["n"]:
            subset = [r for r in rows if r["regime"] == regime and r["n"] == n]
            finite = [r for r in subset if not r["abstain"]]
            successes = sum(int(r["covered"]) for r in subset)
            lo, hi = wilson_interval(successes, len(subset))
            aggregates.append(
                dict(
                    regime=regime,
                    n=n,
                    trials=len(subset),
                    coverage=successes / len(subset),
                    coverage_wilson_low=lo,
                    coverage_wilson_high=hi,
                    abstentions=len(subset) - len(finite),
                    mean_plugin_regret=float(
                        np.mean([r["plugin_regret"] for r in finite])
                    ),
                    mean_robust_regret=float(
                        np.mean([r["robust_regret"] for r in finite])
                    ),
                    bound_violations=sum(int(r["guarantee_violation"]) for r in finite),
                )
            )
    with (out / "estimated-interval-aggregate.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(aggregates[0]))
        w.writeheader()
        w.writerows(aggregates)
    normal = [r for r in rows if r["regime"] == "iid_gaussian"]
    normal_ci = wilson_interval(sum(int(r["covered"]) for r in normal), len(normal))
    conditional_violations = sum(
        int(r["guarantee_violation"]) for r in rows if r["covered"] and not r["abstain"]
    )
    assert normal_ci[0] >= c["thresholds"]["normal_coverage_wilson_low_min"]
    assert conditional_violations == 0
    # Instrument only computation; samples/imports/install are excluded.
    runtime = []
    for n in c["n"]:
        x = np.random.default_rng(42).normal(size=n).tolist()
        for method in ["plugin", "interval_robust"]:
            for rep in range(30):
                tracemalloc.start()
                start = time.perf_counter()
                if method == "plugin":
                    q = optimal_weight(
                        1, 1, 1, math.sqrt(min(float(np.var(x, ddof=1)), 16))
                    )
                else:
                    ci = gaussian_variance_interval(x)
                    assert ci is not None
                    q = robust_weight(1, 1, 1, ci.low, ci.high)
                elapsed = time.perf_counter() - start
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                runtime.append(
                    dict(
                        n=n,
                        method=method,
                        repetition=rep,
                        seconds=elapsed,
                        python_peak_bytes=peak,
                        q=q,
                    )
                )
    with (out / "estimated-interval-runtime.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(runtime[0]))
        w.writeheader()
        w.writerows(runtime)
    summary = dict(
        config=c,
        cases=len(rows),
        raw_shocks=len(shocks),
        normal_coverage=sum(int(r["covered"]) for r in normal) / len(normal),
        normal_wilson95=normal_ci,
        conditional_bound_violations=conditional_violations,
        aggregates=aggregates,
        hardware=platform.platform(),
        python=sys.version,
        versions=dict(
            numpy=np.__version__,
            scipy=scipy.__version__,
            matplotlib=matplotlib.__version__,
        ),
        data_sha256=hashlib.sha256(
            (out / "estimated-shocks.csv.gz").read_bytes()
        ).hexdigest(),
        source_sha256=hashlib.sha256(
            (root / "src/variance_interval.py").read_bytes()
        ).hexdigest(),
        execution_method="Exact loss conditional on simulated training data; no simulated evaluation noise",
    )
    (out / "estimated-interval-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    fig, axs = plt.subplots(1, 2, figsize=(12, 4), layout="constrained")
    for regime, color, marker in zip(
        c["regimes"], ["#0072B2", "#D55E00", "#009E73"], ["o", "s", "^"]
    ):
        sub = [a for a in aggregates if a["regime"] == regime]
        means = [a["coverage"] for a in sub]
        axs[0].errorbar(
            c["n"],
            means,
            yerr=[
                [a["coverage"] - a["coverage_wilson_low"] for a in sub],
                [a["coverage_wilson_high"] - a["coverage"] for a in sub],
            ],
            label=regime,
            color=color,
            marker=marker,
            capsize=3,
        )
        axs[1].plot(
            c["n"],
            [a["mean_robust_regret"] - a["mean_plugin_regret"] for a in sub],
            label=regime,
            color=color,
            marker=marker,
        )
    axs[0].axhline(0.9, color="black", ls="--", label="Nominal90%")
    axs[0].set(
        xlabel="Observaciones históricas n",
        ylabel="Cobertura de varianza futura",
        ylim=(-0.03, 1.03),
        title="Wilson95%; 360simulaciones por punto",
    )
    axs[0].legend(fontsize=7)
    axs[1].axhline(0, color="black", ls="--")
    axs[1].set(
        xlabel="Observaciones históricas n",
        ylabel="Regret medio robusto − plug-in (pérdida)",
        title="Evaluación exacta fuera de muestra temporal",
    )
    axs[1].legend(fontsize=7)
    fig.suptitle("Simulación fija: α=λ=k=1; confianza90%; sin evidencia macro real")
    fig.savefig(out / "estimated-interval.png", dpi=150)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
