"""Deterministic experiments for the collateral/liquidation choice."""

import csv
import json
import platform
import random
import sys
import time
import tracemalloc
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from liquidity import Problem, dense_grid, liquidation_only, solve  # noqa: E402

RESULTS = ROOT / "results"
SEED = 20261022


def write_csv(name: str, rows: list[dict[str, object]]) -> None:
    with (RESULTS / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def row(label: str, method: str, choice: object) -> dict[str, object]:
    return {"scenario": label, "method": method, **choice.__dict__}


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    main_problem = Problem(0.4, 1, 1, 0.5, 0.1, 0.3, 0.1)
    optimal, pure, grid = (
        solve(main_problem),
        liquidation_only(main_problem),
        dense_grid(main_problem, 200_001),
    )
    choices = [
        row("main", "collateral_choice", optimal),
        row("main", "liquidation_only", pure),
        row("main", "dense_grid_200001", grid),
    ]
    write_csv("main_results.csv", choices)

    sensitivity: list[dict[str, object]] = []
    for pledgeable in (0, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8, 1):
        for rate in (0, 0.05, 0.1, 0.25, 0.5, 1, 2):
            problem = Problem(0.4, 1, 1, 0.5, 0.1, pledgeable, rate)
            try:
                choice = solve(problem)
                sensitivity.append(
                    {"pledgeable": pledgeable, "rate": rate, **choice.__dict__}
                )
            except ArithmeticError:
                sensitivity.append(
                    {
                        "pledgeable": pledgeable,
                        "rate": rate,
                        "liquidation": "",
                        "borrowing": "",
                        "price": "",
                        "cost": "",
                        "collateral_slack": "",
                        "liquidity_slack": "",
                    }
                )
    write_csv("sensitivity.csv", sensitivity)

    rng = random.Random(SEED)
    validation: list[dict[str, object]] = []
    max_cost_gap = 0.0
    for index in range(50):
        problem = Problem(
            rng.uniform(0.05, 0.45),
            1,
            1,
            rng.uniform(0.05, 0.6),
            0.1,
            rng.uniform(0.1, 1),
            rng.uniform(0, 2),
        )
        exact, oracle = solve(problem), dense_grid(problem, 50_001)
        gap = oracle.cost - exact.cost
        max_cost_gap = max(max_cost_gap, gap)
        validation.append(
            {
                "case": index,
                "cost_gap_grid_minus_solver": gap,
                "liquidation_error": abs(oracle.liquidation - exact.liquidation),
                "feasible": exact.collateral_slack >= -1e-9,
            }
        )
    write_csv("validation.csv", validation)

    stability: list[dict[str, object]] = []
    reference = solve(main_problem)
    for points in (101, 1_001, 10_001, 100_001, 1_000_001):
        approx = dense_grid(main_problem, points)
        stability.append(
            {
                "points": points,
                "liquidation_error": abs(approx.liquidation - reference.liquidation),
                "cost_error": approx.cost - reference.cost,
            }
        )
    write_csv("stability.csv", stability)

    costs: list[dict[str, object]] = []
    for count in (100, 1_000, 10_000):
        problems = [
            Problem(
                0.2 + 0.2 * (i % 11) / 10, 1, 1, 0.5, 0.1, 0.3 + 0.4 * (i % 7) / 6, 0.1
            )
            for i in range(count)
        ]
        for method, points in (("candidate_solver", 0), ("grid_101", 101)):
            durations, peaks = [], []
            for _ in range(3):
                tracemalloc.start()
                start = time.perf_counter()
                output = (
                    [solve(p) for p in problems]
                    if not points
                    else [dense_grid(p, points) for p in problems]
                )
                durations.append(time.perf_counter() - start)
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                peaks.append(peak)
                assert len(output) == count
            costs.append(
                {
                    "cases": count,
                    "method": method,
                    "median_seconds": sorted(durations)[1],
                    "median_peak_python_bytes": sorted(peaks)[1],
                }
            )
    write_csv("costs.csv", costs)

    ablations = []
    for label, problem in (
        ("abundant_collateral", Problem(0.4, 1, 1, 0.5, 0.1, 0.8, 0.1)),
        ("free_borrowing", Problem(0.4, 1, 1, 0.5, 0.1, 0.8, 0.0)),
        ("high_borrowing_rate", Problem(0.4, 1, 1, 0.5, 0.1, 0.8, 2)),
        ("no_price_impact", Problem(0.4, 1, 1, 0, 0.1, 0.3, 0.1)),
    ):
        ablations.append(row(label, "collateral_choice", solve(problem)))
    write_csv("ablations.csv", ablations)

    metadata = {
        "seed": SEED,
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "random_cases": 50,
        "max_grid_cost_gap": max_cost_gap,
        "objective": "private reduced-form funding cost; not welfare",
    }
    (RESULTS / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    valid = [x for x in sensitivity if x["cost"] != ""]
    for rate, color in (
        (0.05, "#315b7d"),
        (0.1, "#d28b36"),
        (0.5, "#7b8f35"),
        (2, "#9b5c7a"),
    ):
        subset = [x for x in valid if x["rate"] == rate]
        axes[0].plot(
            [x["pledgeable"] for x in subset],
            [x["liquidation"] for x in subset],
            marker="o",
            label=f"rate={rate:g}",
            color=color,
        )
    axes[0].set(
        xlabel="Pledgeable fraction",
        ylabel="Optimal liquidation (asset units)",
        title="Collateral capacity changes funding mix",
    )
    axes[0].legend(frameon=False)
    axes[1].bar(
        ["Mixed choice", "Liquidation only"],
        [optimal.cost, pure.cost],
        color=["#315b7d", "#d28b36"],
    )
    axes[1].set(ylabel="Private funding cost", title="Main synthetic fixture")
    axes[1].set_ylim(0, max(pure.cost, optimal.cost) * 1.25)
    for ax in axes:
        ax.grid(axis="y", alpha=0.25)
    fig.suptitle("Collateral Liquidity Choice — synthetic reduced-form experiment")
    fig.tight_layout()
    fig.savefig(RESULTS / "comparison.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
