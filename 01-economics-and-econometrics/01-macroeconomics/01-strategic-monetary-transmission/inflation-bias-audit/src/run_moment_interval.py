"""Audit coverage/decision cost of a fourth-moment-bound variance interval."""

import csv
import gzip
import hashlib
import json
import platform
import time
import tracemalloc
from pathlib import Path
from typing import Any
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .moment_interval import bounded_kurtosis_interval
from .variance_interval import wilson_interval
from .ambiguity import robust_weight, regret, worst_regret


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "results"
    config = json.loads((root / "moment-config.json").read_text())
    data: dict[int, list[float]] = {}
    with gzip.open(out / "estimated-shocks.csv.gz", "rt") as f:
        for row in csv.DictReader(f):
            data.setdefault(int(row["sample_id"]), []).append(float(row["shock"]))
    old = list(csv.DictReader((out / "estimated-interval.csv").open()))
    rows: list[dict[str, Any]] = []
    for r in old:
        ci = bounded_kurtosis_interval(
            data[int(r["sample_id"])], config["kurtosis_bound"], config["confidence"]
        )
        truth = float(r["future_variance"])
        q = None if ci is None else robust_weight(1, 1, 1, ci.low, ci.high)
        actual = None if q is None else regret(q, 1, 1, 1, truth)
        bound = (
            None
            if q is None or ci is None
            else worst_regret(q, 1, 1, 1, ci.low, ci.high)
        )
        covered = bool(ci is not None and ci.low <= truth <= ci.high)
        rows.append(
            dict(
                sample_id=int(r["sample_id"]),
                seed=int(r["seed"]),
                n=int(r["n"]),
                regime=r["regime"],
                truth=truth,
                abstain=int(ci is None),
                covered=int(covered),
                width=None if ci is None else ci.high - ci.low,
                radius=None if ci is None else ci.radius,
                q=q,
                regret=actual,
                bound=bound,
                conditional_violation=int(
                    covered
                    and actual is not None
                    and bound is not None
                    and actual > bound + 1e-10
                ),
                gaussian_covered=int(r["covered"]),
                gaussian_width=float(r["high"]) - float(r["low"]),
                gaussian_regret=float(r["robust_regret"]),
                plugin_regret=float(r["plugin_regret"]),
            )
        )
    with (out / "moment-cases.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    aggregates = []
    for regime in ["iid_gaussian", "iid_student_t5", "variance_break_x4"]:
        for n in [16, 64, 256]:
            sub = [r for r in rows if r["regime"] == regime and r["n"] == n]
            finite = [r for r in sub if not r["abstain"]]
            lo, hi = wilson_interval(sum(r["covered"] for r in sub), len(sub))
            aggregates.append(
                dict(
                    regime=regime,
                    n=n,
                    trials=len(sub),
                    coverage=sum(r["covered"] for r in sub) / len(sub),
                    wilson_low=lo,
                    wilson_high=hi,
                    abstentions=len(sub) - len(finite),
                    gaussian_coverage=float(
                        np.mean([r["gaussian_covered"] for r in sub])
                    ),
                    mean_width=float(np.mean([r["width"] for r in finite])),
                    gaussian_width=float(np.mean([r["gaussian_width"] for r in sub])),
                    mean_regret=float(np.mean([r["regret"] for r in finite])),
                    gaussian_regret=float(np.mean([r["gaussian_regret"] for r in sub])),
                    plugin_regret=float(np.mean([r["plugin_regret"] for r in sub])),
                )
            )
    assert all(
        a["wilson_low"] >= 0.85
        for a in aggregates
        if a["regime"] != "variance_break_x4"
    )
    assert sum(r["conditional_violation"] for r in rows) == 0
    sensitivity = []
    for k in config["sensitivity_k"]:
        for regime in ["iid_gaussian", "iid_student_t5"]:
            sub = [r for r in old if r["regime"] == regime and int(r["n"]) == 256]
            coverage_count = 0
            widths = []
            for r in sub:
                ci = bounded_kurtosis_interval(data[int(r["sample_id"])], k, 0.9)
                coverage_count += (
                    ci is not None and ci.low <= float(r["future_variance"]) <= ci.high
                )
                if ci is not None:
                    widths.append(ci.high - ci.low)
            sensitivity.append(
                dict(
                    k=k,
                    regime=regime,
                    n=256,
                    coverage=coverage_count / len(sub),
                    mean_width=float(np.mean(widths)),
                )
            )
    runtime = []
    for n in [16, 64, 256]:
        x = data[next(int(r["sample_id"]) for r in old if int(r["n"]) == n)]
        for rep in range(30):
            tracemalloc.start()
            start = time.perf_counter()
            ci = bounded_kurtosis_interval(x)
            assert ci is not None
            q = robust_weight(1, 1, 1, ci.low, ci.high)
            elapsed = time.perf_counter() - start
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            runtime.append(
                dict(n=n, repetition=rep, seconds=elapsed, python_peak_bytes=peak, q=q)
            )
    for name, values in [
        ("moment-aggregate.csv", aggregates),
        ("moment-sensitivity.csv", sensitivity),
        ("moment-runtime.csv", runtime),
    ]:
        with (out / name).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(values[0]))
            w.writeheader()
            w.writerows(values)
    summary = dict(
        config=config,
        cases=len(rows),
        aggregates=aggregates,
        sensitivity=sensitivity,
        conditional_violations=sum(r["conditional_violation"] for r in rows),
        hardware=platform.platform(),
        numpy=np.__version__,
        data_sha256=hashlib.sha256(
            (out / "estimated-shocks.csv.gz").read_bytes()
        ).hexdigest(),
        source_sha256=hashlib.sha256(
            (root / "src/moment_interval.py").read_bytes()
        ).hexdigest(),
    )
    (out / "moment-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    fig, axs = plt.subplots(1, 3, figsize=(14, 4), layout="constrained")
    for regime, color, marker in [
        ("iid_gaussian", "#0072B2", "o"),
        ("iid_student_t5", "#D55E00", "s"),
        ("variance_break_x4", "#009E73", "^"),
    ]:
        a = [v for v in aggregates if v["regime"] == regime]
        ns = [v["n"] for v in a]
        axs[0].plot(
            ns,
            [v["coverage"] for v in a],
            marker=marker,
            color=color,
            label=regime + " K9",
        )
        axs[0].plot(
            ns,
            [v["gaussian_coverage"] for v in a],
            ls="--",
            color=color,
            label=regime + " chi²",
        )
        axs[1].plot(
            ns, [v["mean_width"] for v in a], marker=marker, color=color, label=regime
        )
        axs[2].plot(
            ns,
            [v["mean_regret"] - v["gaussian_regret"] for v in a],
            marker=marker,
            color=color,
            label=regime,
        )
    axs[0].axhline(0.9, color="black", ls=":")
    axs[0].set(
        xlabel="Observaciones históricas n",
        ylabel="Cobertura de varianza futura",
        ylim=(-0.03, 1.03),
        title="K9 frente a chi² (mismos fixtures)",
    )
    axs[0].legend(fontsize=6)
    axs[1].set(
        xlabel="Observaciones históricas n",
        ylabel="Amplitud media (shock²)",
        title="Coste: intervalos muy amplios",
    )
    axs[2].axhline(0, color="black", ls=":")
    axs[2].set(
        xlabel="Observaciones históricas n",
        ylabel="Regret medio K9 − chi² (pérdida)",
        title="Mayor cobertura no garantiza utilidad",
    )
    axs[2].legend(fontsize=6)
    fig.suptitle(
        "Simulación sintética; α=λ=k=1; confianza90%; cota externa de kurtosisK9"
    )
    fig.savefig(out / "moment-interval.png", dpi=150)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
