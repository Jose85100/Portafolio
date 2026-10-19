"""Version-pinned regression and current Stage3 oracle reconciliation."""

import hashlib
import json
import random
import statistics
import time
import tracemalloc
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from benchmarks.run import reference, write_csv
from src.baseline import CURRENT_SOURCE, SOURCE, legacy_ecl
from src.migration import current, reconciliation
from src.model import shortfall

PROJECT = Path(__file__).resolve().parents[1]


def main() -> None:
    out = PROJECT / "results"
    cases = pd.read_csv(out / "accuracy.csv")
    rows: list[dict[str, Any]] = []
    for c in cases.to_dict("records"):
        gross = np.array([100.0])
        recovery = 100 * c["recovery_fraction"]
        p = pd.DataFrame(
            {
                "loan_id": [1],
                "pd_12m": c["pd12"],
                "pd_origen": c["pd12"],
                "dpd": 95,
                "ead": gross,
                "lgd_base": c["lgd_pv"],
                "ccf": 0.0,
                "undrawn": 0.0,
                "gross_carrying_amount": gross,
                "recovery_times": [(float(c["lag_years"]),)],
                "recovery_cashflows": [(recovery,)],
            }
        )
        new = current.ecl_componentes(p, "base", int(c["horizon"]), c["eir"])
        value = float(new.ecl.iloc[0])
        oracle = reference(100.0, recovery, int(c["lag_years"]), c["eir"])
        relative = abs(value - oracle) / oracle if oracle else abs(value)
        assert relative <= 1e-12
        assert new.ecl_basis.iloc[0] == "funded_recovery_cashflows"
        assert new[["ecl_12m", "ecl_lifetime"]].isna().all().all()
        rows.append({**c, "current_engine_ecl": value, "current_relative_error": relative})
    write_csv(out / "migration-stage3.csv", rows)
    p = current.cartera_sintetica(300, 20261019)
    p["pd_12m"], p["pd_origen"], p["lgd_base"] = 0.05, 0.04, 0.4
    p["recovery_times"] = [(2.0,)] * len(p)
    p["recovery_cashflows"] = [(float(g) * 0.6,) for g in p.gross_carrying_amount]
    p.loc[p.index[np.arange(len(p)) % 3 == 2], "lgd_base"] = 1 - 0.6 / 1.1**2
    p["dpd"] = np.tile([0, 35, 95], 100)
    p.index = np.arange(300)[::-1]
    reconciled = reconciliation(p)
    reconciled.to_csv(out / "migration-by-loan.csv", index=False)
    p.to_json(out / "migration-inputs.json", orient="records", indent=2)
    performing_error = float(np.abs(reconciled.loc[reconciled.stage.ne(3), "relative_difference"]).max())
    assert performing_error <= 1e-12
    # Explicit negative ablation: subtracting two rounded values loses delay loss.
    tiny = current.credit_impaired_shortfall(100.0, [100.0], [1.0], 1e-18)
    naive = 100 - float(np.sum(np.array([100.0]) * np.exp(-np.log1p(1e-18))))
    assert naive == 0 and tiny["raw_shortfall"] > 0
    rng = random.Random(20261019)
    timing: list[dict[str, Any]] = []
    for n in [1, 32, 256]:
        g = np.full(n, 100.0)
        cash = np.full((n, 1), 60.0)
        pv_lgd = shortfall(g, cash, [2], 0.1) / g
        p = pd.DataFrame(
            {
                "loan_id": np.arange(n),
                "pd_12m": 0.05,
                "pd_origen": 0.04,
                "dpd": 95,
                "ead": g,
                "lgd_base": pv_lgd,
                "ccf": 0.0,
                "undrawn": 0.0,
                "gross_carrying_amount": g,
                "recovery_times": [(2.0,)] * n,
                "recovery_cashflows": [(60.0,)] * n,
            }
        )
        methods = {
            "historical_engine": lambda: legacy_ecl(g, pv_lgd, 0.05, 5, 0.1),
            "current_engine": lambda: current.ecl_componentes(p),
            "batch_oracle_route": lambda: shortfall(g, cash, [2], 0.1),
        }
        for fn in methods.values():
            fn()
        for rep in range(7):
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
    write_csv(out / "migration-performance.csv", timing)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for stage in [1, 2, 3]:
        sub = reconciled[reconciled.stage.eq(stage)]
        axes[0].scatter(
            sub.ecl_old,
            sub.ecl,
            label=f"Stage {stage}",
            alpha=0.6,
            s=18,
            marker={1: "o", 2: "s", 3: "^"}[stage],
            color={1: "#24557a", 2: "#777777", 3: "#b55b22"}[stage],
        )
    top = float(max(reconciled.ecl.max(), reconciled.ecl_old.max())) * 1.05
    axes[0].plot([0, top], [0, top], "--", color="#222222", linewidth=1)
    axes[0].set(
        xlabel="ECL histórica por contrato",
        ylabel="ECL actual por contrato",
        title="Misma población, 100 contratos por stage",
        xlim=(0, top),
        ylim=(0, top),
    )
    axes[0].legend(fontsize=8)
    selected = [
        r
        for r in rows
        if r["pd12"] == 0.05
        and r["recovery_fraction"] == 0.5
        and r["lag_years"] == 1
        and r["eir"] == 0.1
        and r["horizon"] == 5
    ]
    example = selected[0]
    values = [example["baseline_ecl"], example["current_engine_ecl"], example["decimal_oracle"]]
    bars = axes[1].bar(["Histórico", "Actual", "Decimal"], values, color=["#24557a", "#b55b22", "#777777"])
    for bar, value in zip(bars, values, strict=True):
        axes[1].text(bar.get_x() + bar.get_width() / 2, value + 1, f"{value:.2f}", ha="center")
    axes[1].set(ylabel="ECL por 100 unidades", ylim=(0, 65), title="Recuperar 50 al año 1; EIR10%, PD5%")
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.2)
        ax.set_axisbelow(True)
    fig.savefig(out / "migration.png", dpi=150)
    fig.savefig(out / "migration.svg")
    svg = out / "migration.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    plt.close(fig)
    summary = {
        "date": "2026-10-19",
        "seed": 20261019,
        "stage3_cases": len(rows),
        "stage3_max_relative_error": max(r["current_relative_error"] for r in rows),
        "mixed_loans": len(reconciled),
        "stage_counts": reconciled.stage.value_counts().to_dict(),
        "stage12_max_relative_change": performing_error,
        "tiny_rate_subtractive": naive,
        "tiny_rate_current": tiny["raw_shortfall"],
        "frozen_commit": "f03f242222a0410f4558fb0522544afcd9ebb4f8",
        "historical_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "current_sha256": hashlib.sha256(CURRENT_SOURCE.read_bytes()).hexdigest(),
        "performance_rows": len(timing),
        "medians_ms": {
            f"{n}/{m}": statistics.median(
                r["nanoseconds"] for r in timing if r["n"] == n and r["method"] == m
            )
            / 1e6
            for n in [1, 32, 256]
            for m in ["historical_engine", "current_engine", "batch_oracle_route"]
        },
    }
    (out / "migration-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
