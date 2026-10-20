"""Executed joint-vs-frozen experiment and independent nested root finding."""

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
sys.path[:0] = [
    str(ROOT / "src"),
    str(ROOT.parent / "sovereign-clearing-audit/src"),
    str(ROOT.parent / "fire-sale-price-audit/src"),
]
from coupled import Economy, Solution, accounts, census, evaluate  # noqa: E402
from clearing import Network, bracket, rational_clear  # noqa: E402
from market import Market, equilibria, sales as old_sales  # noqa: E402


def save(name, rows):
    with (ROOT / "results" / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def nested(e, q):
    net = Network(np.array(e.liabilities), np.array(e.outside))
    result = bracket(net, np.array(e.cash) + q * np.array(e.stock), tolerance=1e-12)
    payments = tuple(map(float, result.payments))
    _, qnew, sale = evaluate(e, q, payments)
    return Solution(q, payments, sale, max(abs(qnew - q), result.residual_l1))


def grid(e, size=501):
    points = np.linspace(e.floor, e.fundamental, size)
    values = [
        evaluate(e, float(q), nested(e, float(q)).payments)[1] - q for q in points
    ]
    found = []
    for i, (q, f) in enumerate(zip(points, values)):
        if abs(f) < 1e-11:
            found.append(float(q))
        if i and f * values[i - 1] < 0:
            found.append(
                brentq(
                    lambda p: evaluate(e, p, nested(e, p).payments)[1] - p,
                    points[i - 1],
                    q,
                    xtol=1e-12,
                )
            )
    unique = []
    for q in sorted(found):
        if not unique or abs(q - unique[-1]) > 1e-9:
            unique.append(q)
    return unique


def upper(e, budget=10000):
    q = e.fundamental
    for _ in range(budget):
        r = nested(e, q)
        new = evaluate(e, q, r.payments)[1]
        if abs(q - new) < 1e-12:
            return [new]
        q = new
    raise RuntimeError("Outer iteration exhausted budget; not a solution")


def frozen(e):
    receipts = tuple(
        sum(e.pi[j][i] * e.total[j] for j in range(len(e.outside)))
        for i in range(len(e.outside))
    )
    m = Market(
        tuple(c + r for c, r in zip(e.cash, receipts)),
        e.total,
        e.stock,
        e.impact,
        e.fundamental,
        e.floor,
    )
    roots = equilibria(m)
    result = []
    for root in roots:
        q = root.price
        payments = tuple(
            min(t, c + r + q * s)
            for t, c, r, s in zip(e.total, e.cash, receipts, e.stock)
        )
        pn, qn, sale = evaluate(e, q, payments)
        residual = max(abs(qn - q), *(abs(p - pp) for p, pp in zip(payments, pn)))
        result.append(Solution(q, payments, old_sales(m, q), residual))
    return result


def row(e, r):
    return dict(
        price=r.price,
        payments=json.dumps(r.payments),
        sales=json.dumps(r.sales),
        defaults=sum(p < t - 1e-9 for p, t in zip(r.payments, e.total)),
        residual=r.residual,
        **accounts(e, r),
    )


def run():
    (ROOT / "results").mkdir(exist_ok=True)
    e = Economy(((0.0, 0.1), (0.1, 0.0)), (0.1, 0.1), (0.0, 0.02), (1.0, 0.2), 0.8)
    config = dict(
        seed=20261020,
        economy=asdict(e),
        candidate_tolerance=1e-8,
        h1="Three analytical joint roots with price error<=1e-10 and residual<=1e-9",
        h2="Frozen contractual receipts understates low-root external unpaid by>=.05; not jointly feasible",
        regimes="3^n, n<=4; external debtor share>=1%",
        grid_sizes=[101, 501],
        repeats=3,
    )
    (ROOT / "results/config.json").write_text(json.dumps(config, indent=2) + "\n")
    joint = census(e)
    save("equilibria.csv", [row(e, r) for r in joint])
    baselines = [dict(method="frozen_receipts", **row(e, r)) for r in frozen(e)]
    baselines.append(dict(method="fixed_price_EN", **row(e, nested(e, 1.0))))
    baselines.append(dict(method="upper_nested", **row(e, nested(e, upper(e)[0]))))
    save("baselines.csv", baselines)
    expected = [0.05, (0.92 - np.sqrt(0.3984)) / 2, (1 + np.sqrt(0.424)) / 2]
    assert (
        len(joint) == 3
        and max(abs(r.price - q) for r, q in zip(joint, expected)) < 1e-10
    )
    assert max(r.residual for r in joint) < 1e-9
    assert (
        accounts(e, joint[0])["outside_unpaid"]
        - accounts(e, frozen(e)[0])["outside_unpaid"]
        >= 0.05
    )
    randoms = []
    rng = random.Random(20261020)
    for index in range(12):
        case = replace(
            e,
            cash=(rng.randrange(0, 8) / 100, rng.randrange(0, 8) / 100),
            stock=(rng.randrange(5, 15) / 10, rng.randrange(1, 10) / 10),
            impact=rng.randrange(3, 10) / 10,
        )
        reference = census(case)
        observed = grid(case, 501)
        distances = [min(abs(q - r.price) for r in reference) for q in observed]
        error = max(distances, default=0.0)
        matched = sum(any(abs(r.price - q) < 1e-7 for q in observed) for r in reference)
        randoms.append(
            dict(
                case=index,
                cash=json.dumps(case.cash),
                stock=json.dumps(case.stock),
                impact=case.impact,
                enum_count=len(reference),
                grid_count=len(observed),
                matched=matched,
                max_grid_to_enum_error=error,
            )
        )
        assert error < 1e-7 and matched == len(reference)
    save("nested_crosscheck.csv", randoms)
    # Reduction to both prior executable MVPs, not merely a copied formula.
    regression = []
    for r in joint:
        net = Network(np.array(e.liabilities), np.array(e.outside))
        exact = rational_clear(net, np.array(e.cash) + r.price * np.array(e.stock))
        regression.append(
            dict(
                kind="prior_EN_payments",
                price=r.price,
                error=max(abs(float(x) - p) for x, p in zip(exact, r.payments)),
            )
        )
    no_edges = replace(e, liabilities=((0.0, 0.0), (0.0, 0.0)))
    prior = equilibria(
        Market(no_edges.cash, no_edges.outside, no_edges.stock, no_edges.impact)
    )
    for r, p in zip(census(no_edges), prior):
        regression.append(
            dict(
                kind="prior_no_edges_prices",
                price=r.price,
                error=abs(r.price - p.price),
            )
        )
    save("repo_regression.csv", regression)
    stability = []
    for tolerance in [1e-6, 1e-9, 1e-12]:
        for r in joint:
            checked = bracket(
                net, np.array(e.cash) + r.price * np.array(e.stock), tolerance=tolerance
            )
            pnew, qnew, _ = evaluate(e, r.price, tuple(map(float, checked.payments)))
            stability.append(
                dict(
                    tolerance=tolerance,
                    price=r.price,
                    inner_iterations=checked.iterations,
                    payment_error_l1=float(
                        np.abs(checked.payments - np.array(r.payments)).sum()
                    ),
                    induced_price_error=abs(qnew - r.price),
                    bracket_width=checked.width_l1,
                )
            )
    save("tolerance_stability.csv", stability)
    costs = []
    for n in [2, 3, 4]:
        debt = tuple(
            tuple(0.2 / n if j == (i + 1) % n else 0.0 for j in range(n))
            for i in range(n)
        )
        case = Economy(
            debt,
            tuple(0.2 / n for _ in range(n)),
            (0.0,) * n,
            tuple(2 / n for _ in range(n)),
            0.8,
        )
        reference = census(case)
        for name, function in {
            "regime_census": lambda: [r.price for r in census(case)],
            "nested_grid101": lambda: grid(case, 101),
            "upper_nested": lambda: upper(case),
        }.items():
            for repeat in range(3):
                tracemalloc.start()
                start = time.perf_counter()
                prices = function()
                elapsed = time.perf_counter() - start
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                costs.append(
                    dict(
                        n=n,
                        method=name,
                        repeat=repeat,
                        regimes=3**n,
                        seconds=elapsed,
                        python_peak_bytes=peak,
                        roots_recovered=sum(
                            any(abs(r.price - q) < 1e-7 for q in prices)
                            for r in reference
                        ),
                        reference_roots=len(reference),
                    )
                )
    save("costs.csv", costs)
    stress = []
    for gap in np.linspace(0.0, 0.10, 21):
        case = replace(e, cash=(float(gap), 0.02))
        for name, rs in [("joint", census(case)), ("frozen", frozen(case))]:
            for r in rs:
                stress.append(dict(cash_bank1=float(gap), method=name, **row(case, r)))
    save("cash_sweep.csv", stress)
    ablations = []
    cases = [
        ("no_edges", no_edges),
        ("zero_impact", replace(e, impact=0.0)),
        ("enough_cash", replace(e, cash=(1.0, 1.0))),
        ("symmetric", replace(e, cash=(0.0, 0.0), stock=(1.0, 1.0))),
        ("tangent_no_edges", Economy(((0.0,),), (0.3125,), (0.0,), (2.0,), 0.8)),
    ]
    for name, case in cases:
        reference = census(case)
        observed = grid(case, 101)
        ablations.append(
            dict(
                case=name,
                joint_prices=json.dumps([r.price for r in reference]),
                grid_prices=json.dumps(observed),
                roots_missed=sum(
                    not any(abs(r.price - q) < 1e-7 for q in observed)
                    for r in reference
                ),
            )
        )
    save("ablations.csv", ablations)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), layout="constrained")
    positions = np.arange(3)
    axes[0].bar(
        positions - 0.17,
        [accounts(e, r)["outside_unpaid"] for r in joint],
        width=0.34,
        color="#22658c",
        label="Acoplado",
    )
    axes[0].bar(
        positions + 0.17,
        [accounts(e, r)["outside_unpaid"] for r in frozen(e)],
        width=0.34,
        color="#bd781e",
        hatch="//",
        label="Cobros contractuales",
    )
    axes[0].set(
        xticks=positions,
        xticklabels=["Precio bajo", "Interior", "Precio alto"],
        ylabel="Impago externo (numeraire)",
        title="Pagos y precios resueltos conjuntamente",
        ylim=(0, 0.135),
    )
    axes[0].legend()
    axes[0].annotate(
        "Ablation no factible\ncomo equilibrio conjunto",
        xy=(0.17, 0.06),
        xytext=(0.45, 0.095),
        arrowprops=dict(arrowstyle="-", color="#444444"),
        fontsize=9,
    )
    for name, color, marker in [("joint", "#22658c", "o"), ("frozen", "#bd781e", "x")]:
        selected = [r for r in stress if r["method"] == name]
        axes[1].scatter(
            [r["cash_bank1"] for r in selected],
            [r["price"] for r in selected],
            color=color,
            marker=marker,
            s=22,
            label=name,
        )
    axes[1].set(
        xlabel="Caja del banco1 (numeraire)",
        ylabel="Precio de equilibrio",
        title="Sensibilidad y ramas; no probabilidades",
    )
    axes[1].legend()
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.15)
    fig.savefig(ROOT / "results/comparison.png", dpi=160)
    plt.close(fig)
    cpu = Path("/proc/cpuinfo")
    model = (
        next(
            (
                line.split(":", 1)[1].strip()
                for line in cpu.read_text().splitlines()
                if line.startswith("model name")
            ),
            "not exposed",
        )
        if cpu.exists()
        else "not exposed"
    )
    meta = dict(
        python=sys.version,
        platform=platform.platform(),
        cpu=model,
        logical_cpus=os.cpu_count(),
        seed=20261020,
        base_commit="dd5dc42984ca98ecf3ccda47a21dfd4008afe0bb",
        memory="Python allocations via tracemalloc, not RSS/native",
        timing="wall with tracemalloc,3 paired repeats",
        config_sha256=hashlib.sha256(
            (ROOT / "results/config.json").read_bytes()
        ).hexdigest(),
    )
    (ROOT / "results/metadata.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(
        json.dumps(
            dict(
                roots=[row(e, r) for r in joint],
                crosschecks=len(randoms),
                max_crosscheck_error=max(r["max_grid_to_enum_error"] for r in randoms),
                max_repo_error=max(r["error"] for r in regression),
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    run()
