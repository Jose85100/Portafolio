import csv
import hashlib
import itertools
import json
import platform
import random
import statistics
import time
import tracemalloc
from decimal import Decimal, localcontext
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from src.baseline import SOURCE, legacy_ecl
from src.model import scenario_shortfall, shortfall

PROJECT = Path(__file__).resolve().parents[1]
Row = dict[str, Any]


def write_csv(path: Path, rows: list[Row]) -> None:
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def reference(gross: float, recovery: float, lag: int, rate: float) -> float:
    with localcontext() as ctx:
        ctx.prec = 70
        d = Decimal.from_float
        return float(d(gross) - d(recovery) / (1 + d(rate)) ** lag)


def main() -> None:
    out = PROJECT / "results"
    out.mkdir(exist_ok=True)
    config: Row = {
        "seed": 20261018,
        "gross": 100.0,
        "pd12": [0.01, 0.05, 0.2, 0.5],
        "recovery_fractions": [0.2, 0.5, 0.8, 1.0],
        "lag_years": [0, 1, 3],
        "eir": [0.0, 0.1, 0.2],
        "horizons": [1, 5, 10],
        "repeats": 7,
        "n": [1, 32, 256, 2048],
        "oracle_relative_tolerance": 1e-12,
    }
    (out / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    rows: list[Row] = []
    for pd12, fraction, lag, rate, horizon in itertools.product(
        config["pd12"], config["recovery_fractions"], config["lag_years"], config["eir"], config["horizons"]
    ):
        g = np.array([100.0])
        recovery = 100 * fraction
        new = float(shortfall(g, [[recovery]], [lag], rate)[0])
        oracle = reference(100.0, recovery, lag, rate)
        lgd = new / 100
        old = float(legacy_ecl(g, np.array([lgd]), pd12, horizon, rate)[0])
        mass = 1 - (1 - pd12) ** sum(1.1**year for year in range(horizon))
        assert abs(new - oracle) <= 1e-12 * max(oracle, 1e-300)
        assert old <= new + 1e-10
        rows.append(
            {
                "pd12": pd12,
                "recovery_fraction": fraction,
                "lag_years": lag,
                "eir": rate,
                "horizon": horizon,
                "gross": 100.0,
                "lgd_pv": lgd,
                "baseline_ecl": old,
                "cash_shortfall": new,
                "decimal_oracle": oracle,
                "relative_error": abs(new - oracle) / oracle if oracle else 0.0,
                "baseline_relative_bias": (old / oracle - 1) if oracle else None,
                "future_pd_no_extra_discount": mass * new,
                "certain_default_extra_discount": new / (1 + rate),
            }
        )
    write_csv(out / "accuracy.csv", rows)
    g = np.array([100.0])
    example = float(shortfall(g, [[60.0]], [2], 0.1)[0])
    examples = {
        "gross": 100,
        "recovery": 60,
        "recovery_lag": 2,
        "eir": 0.1,
        "pd12": 0.05,
        "future_pd_horizon": 5,
        "cash_shortfall": example,
        "baseline_ecl": float(legacy_ecl(g, np.array([example / 100]), 0.05, 5, 0.1)[0]),
        "certainty_but_extra_discount": example / 1.1,
        "scenario_ecl": float(scenario_shortfall(g, [[[80]], [[40]]], [2], 0.1, [0.6, 0.4])[0]),
        "tiny_rate_stable": float(shortfall(g, [[100]], [1], 1e-18)[0]),
        "tiny_rate_subtractive": 100 - 100 / (1 + 1e-18),
    }
    (out / "example.json").write_text(json.dumps(examples, indent=2) + "\n")
    rng = random.Random(config["seed"])
    timing: list[Row] = []
    for n in config["n"]:
        gross = np.full(n, 100.0)
        cash = np.full((n, 1), 60.0)
        lgd_pv = shortfall(gross, cash, [2], 0.1) / gross
        methods = {
            "parent_engine": lambda: legacy_ecl(gross, lgd_pv, 0.05, 5, 0.1),
            "cashflow_batch": lambda: shortfall(gross, cash, [2], 0.1),
        }
        for fn in methods.values():
            fn()
        for rep in range(config["repeats"]):
            order = list(methods)
            rng.shuffle(order)
            for position, name in enumerate(order):
                start = time.perf_counter_ns()
                methods[name]()
                elapsed = time.perf_counter_ns() - start
                tracemalloc.start()
                methods[name]()
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                timing.append(
                    {
                        "n": n,
                        "rep": rep,
                        "order": position,
                        "method": name,
                        "nanoseconds": elapsed,
                        "allocated_peak_bytes": peak,
                    }
                )
    write_csv(out / "performance.csv", timing)
    selected = [
        r
        for r in rows
        if r["recovery_fraction"] == 0.5 and r["lag_years"] == 1 and r["eir"] == 0.1 and r["horizon"] == 5
    ]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    for name, label, color, marker in [
        ("baseline_ecl", "Motor actual: default futuro", "#24557a", "o"),
        ("cash_shortfall", "Activo ya incumplido: flujos", "#b55b22", "s"),
    ]:
        axes[0].plot(
            [100 * r["pd12"] for r in selected],
            [r[name] for r in selected],
            label=label,
            color=color,
            marker=marker,
        )
    axes[0].set(
        xlabel="PD 12m ingresada (%)",
        ylabel="ECL por 100 unidades",
        ylim=(0, 65),
        title="Misma recuperación y estado actual",
    )
    axes[0].legend(fontsize=8)
    labels = ["Baseline", "Certeza +\ndescuento extra", "Flujos\ncorrectos"]
    values = [examples["baseline_ecl"], examples["certainty_but_extra_discount"], example]
    bars = axes[1].bar(labels, values, color=["#24557a", "#999999", "#b55b22"])
    for bar, value in zip(bars, values, strict=True):
        axes[1].text(bar.get_x() + bar.get_width() / 2, value + 1, f"{value:.2f}", ha="center")
    axes[1].set(ylabel="ECL por 100 unidades", ylim=(0, 65), title="Recuperar 60 en año 2; EIR 10%")
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.2)
        ax.set_axisbelow(True)
    fig.savefig(out / "comparison.svg")
    fig.savefig(out / "comparison.png", dpi=150)
    plt.close(fig)
    summary = {
        "date": "2026-10-18",
        "cases": len(rows),
        "seed": config["seed"],
        "oracle_max_relative_error": max(r["relative_error"] for r in rows),
        "baseline_underestimates": sum(
            r["baseline_relative_bias"] is not None and r["baseline_relative_bias"] < -1e-12 for r in rows
        ),
        "nonzero_reference_cases": sum(r["cash_shortfall"] > 0 for r in rows),
        "performance_rows": len(timing),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "cpu": next(
            (
                line.strip()
                for line in Path("/proc/cpuinfo").read_text().splitlines()
                if line.startswith("model name")
            ),
            "unknown",
        ),
        "baseline_source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "model_sha256": hashlib.sha256((PROJECT / "src/model.py").read_bytes()).hexdigest(),
        "medians_ms": {
            f"{n}/{m}": statistics.median(
                r["nanoseconds"] for r in timing if r["n"] == n and r["method"] == m
            )
            / 1e6
            for n in config["n"]
            for m in ["parent_engine", "cashflow_batch"]
        },
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
