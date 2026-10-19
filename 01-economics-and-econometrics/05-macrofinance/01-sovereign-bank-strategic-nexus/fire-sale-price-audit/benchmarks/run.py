"""Persist synthetic root census, negative ablations and paired costs."""

from dataclasses import asdict, replace
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import sys
import time
import tracemalloc

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from market import Market, balance, equilibria, iterate, update  # noqa: E402


def save(name, rows):
    with (ROOT / "results" / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def grid(m, size=101):
    """Fair numerical baseline, not a claim about literature implementations."""
    points = np.linspace(m.floor, m.fundamental, size)
    values = [update(m, float(q)) - q for q in points]
    roots = []
    for i, (q, f) in enumerate(zip(points, values)):
        if abs(f) < 1e-12:
            roots.append(float(q))
        if i and f * values[i - 1] < 0:
            roots.append(
                brentq(lambda p: update(m, p) - p, points[i - 1], q, xtol=1e-14)
            )
    return sorted({round(q, 11) for q in roots})


def run():
    (ROOT / "results").mkdir(exist_ok=True)
    m = Market((0.0, 0.0), (0.1, 0.1), (1.0, 1.0), 0.8)
    config = dict(
        seed=20261019,
        market=asdict(m),
        price_tolerance=1e-10,
        iteration_tolerance=1e-12,
        iteration_budget=10000,
        h1="Main fixture roots .05,.2,.8 within1e-10; upper iteration misses2/3",
        h2="Fold at total funding .3125; enumeration recovers tangent price .5",
        scale_banks=[8, 32, 128],
        repeats=3,
    )
    (ROOT / "results/config.json").write_text(json.dumps(config, indent=2) + "\n")
    main = [{**asdict(r), **balance(m, r.price)} for r in equilibria(m)]
    save("equilibria.csv", main)
    baseline = []
    for name, price in [
        ("fixed_price", 1.0),
        ("upper_iteration", iterate(m, 1.0)[0]),
        ("lower_iteration", iterate(m, m.floor)[0]),
        ("one_price_update", update(m, 1.0)),
    ]:
        baseline.append(
            dict(
                method=name, residual=abs(update(m, price) - price), **balance(m, price)
            )
        )
    save("baselines.csv", baseline)
    sweep = []
    for gap in [i / 1000 for i in range(0, 201, 2)] + [0.15625]:
        case = replace(m, debt=(gap, gap))
        for r in equilibria(case):
            sweep.append({"gap_each": gap, **asdict(r), **balance(case, r.price)})
    save("funding_sweep.csv", sweep)
    ablations = []
    for label, case in [
        ("main", m),
        ("zero_impact", replace(m, impact=0.0)),
        ("cash_covers_debt", replace(m, cash=(0.1, 0.1))),
        ("fold", replace(m, debt=(0.15625, 0.15625))),
        ("near_fold", replace(m, debt=(0.15624999, 0.15624999))),
        ("higher_floor", replace(m, floor=0.3)),
    ]:
        reference = [r.price for r in equilibria(case)]
        for size in [101, 1001]:
            observed = grid(case, size)
            matched = sum(any(abs(q - p) < 1e-8 for p in observed) for q in reference)
            ablations.append(
                dict(
                    case=label,
                    grid_size=size,
                    reference_count=len(reference),
                    grid_count=len(observed),
                    missed=len(reference) - matched,
                    reference=json.dumps(reference),
                    grid=json.dumps(observed),
                )
            )
    save("ablations.csv", ablations)
    # Independent numerical root-finding, screened away from degeneracy.
    rng = random.Random(config["seed"])
    comparisons = []
    for index in range(40):
        case = Market(
            tuple(rng.randrange(0, 20) / 100 for _ in range(4)),
            tuple(rng.randrange(10, 50) / 100 for _ in range(4)),
            tuple(rng.randrange(5, 20) / 10 for _ in range(4)),
            0.3,
        )
        reference = [r.price for r in equilibria(case)]
        observed = grid(case, 4001)
        error = max(min(abs(q - p) for p in observed) for q in reference)
        comparisons.append(
            dict(
                case=index,
                enum_count=len(reference),
                grid_count=len(observed),
                max_price_error=error,
            )
        )
        assert len(reference) == len(observed) and error < 1e-8
    save("numerical_crosscheck.csv", comparisons)
    costs = []
    for n in config["scale_banks"]:
        # Fixed aggregate portfolio/funding: number of banks must not change impact.
        case = Market(
            (0.0,) * n,
            tuple((0.1 + (i % 5) * 0.01) / n for i in range(n)),
            tuple(2 / n for _ in range(n)),
            0.8,
        )
        ref = [r.price for r in equilibria(case)]
        methods = {
            "rational_regimes": lambda: [r.price for r in equilibria(case)],
            "upper_iteration": lambda: [iterate(case, 1.0)[0]],
            "grid101_brent": lambda: grid(case),
        }
        for name, function in methods.items():
            for repeat in range(config["repeats"]):
                tracemalloc.start()
                start = time.perf_counter()
                prices = function()
                elapsed = time.perf_counter() - start
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                recovered = sum(any(abs(q - p) < 1e-8 for p in prices) for q in ref)
                costs.append(
                    dict(
                        n=n,
                        method=name,
                        repeat=repeat,
                        seconds=elapsed,
                        python_peak_bytes=peak,
                        roots_recovered=recovered,
                        reference_roots=len(ref),
                        max_residual=max(abs(update(case, p) - p) for p in prices),
                    )
                )
    save("costs.csv", costs)
    # True reduction to the existing EN component at exogenous price, no interbank links.
    sys.path.insert(0, str(ROOT.parent / "sovereign-clearing-audit/src"))
    from clearing import Network, assets, rational_clear

    net = Network(np.zeros((2, 2)), np.array(m.debt))
    rows = []
    for q in [0.05, 0.2, 0.8, 1.0]:
        p = rational_clear(
            net, assets(net, np.array(m.cash), np.array(m.holdings), 1 - q)
        )
        local = balance(m, q)["paid"]
        rows.append(
            dict(
                price=q,
                en_paid=sum(map(float, p)),
                local_paid=local,
                difference=abs(sum(map(float, p)) - local),
            )
        )
    save("repo_regression.csv", rows)
    assert max(r["difference"] for r in rows) < 1e-12
    # Explicit palette and redundant symbols: no scenario band as statistical CI.
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), layout="constrained")
    qs = np.linspace(m.floor, 1.0, 501)
    axes[0].plot(
        qs,
        [update(m, float(q)) for q in qs],
        color="#22658c",
        label="Actualización F(q)",
    )
    axes[0].plot(qs, qs, color="#444444", linestyle="--", label="Precio q")
    for row in main:
        axes[0].scatter(
            row["price"],
            row["price"],
            color="#bd781e",
            marker="o" if row["stability"] == "stable" else "x",
            s=70,
            zorder=4,
        )
        axes[0].annotate(
            f"{row['price']:.2f}",
            (row["price"], row["price"]),
            xytext=(8, 10 if row["price"] == m.floor else -14),
            textcoords="offset points",
        )
    axes[0].set(
        xlabel="Precio de prueba (numeraire/unidad)",
        ylabel="Precio actualizado",
        title="Un mercado, tres puntos fijos",
        xlim=(0, 1.02),
        ylim=(0, 1.02),
    )
    axes[0].legend(loc="upper left")
    for label, marker, color in [
        ("stable", "o", "#22658c"),
        ("unstable", "x", "#bd781e"),
        ("marginal/kink", "D", "#444444"),
    ]:
        selected = [r for r in sweep if r["stability"] == label]
        axes[1].scatter(
            [2 * r["gap_each"] for r in selected],
            [r["price"] for r in selected],
            marker=marker,
            color=color,
            s=14,
            label=label,
        )
    axes[1].axvline(0.3125, color="#777777", linestyle=":", linewidth=1)
    axes[1].set(
        xlabel="Necesidad total de fondos (numeraire)",
        ylabel="Precio de equilibrio",
        title="Ramas y desaparición del equilibrio alto",
        ylim=(0, 1.05),
    )
    axes[1].legend(loc="upper right", fontsize=8)
    for ax in axes:
        ax.grid(alpha=0.15)
        ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(ROOT / "results/comparison.png", dpi=160)
    plt.close(fig)
    cpuinfo = Path("/proc/cpuinfo")
    model = (
        next(
            (
                line.split(":", 1)[1].strip()
                for line in cpuinfo.read_text().splitlines()
                if line.startswith("model name")
            ),
            "not exposed",
        )
        if cpuinfo.exists()
        else "not exposed"
    )
    meta = dict(
        python=sys.version,
        platform=platform.platform(),
        processor=platform.processor(),
        cpu_model=model,
        cpu_count=os.cpu_count(),
        seed=config["seed"],
        memory="tracemalloc Python allocations; not RSS/native memory",
        timing="wall clock with tracemalloc on;3 paired repetitions;no speedup claim",
        base_commit="f1658d32226a517f2e7e88652120001eeea6f47d",
        config_sha256=hashlib.sha256(
            (ROOT / "results/config.json").read_bytes()
        ).hexdigest(),
    )
    (ROOT / "results/metadata.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(
        json.dumps(
            dict(
                roots=main,
                independent_cases=len(comparisons),
                max_crosscheck_error=max(r["max_price_error"] for r in comparisons),
                repo_regression_max=max(r["difference"] for r in rows),
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    run()
