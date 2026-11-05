"""Reproducible payoff-uncertainty audit for selected mixed equilibria."""

from __future__ import annotations
import csv
import json
import platform
import sys
import time
from pathlib import Path
import matplotlib.pyplot as plt
from src.epsilon_robustness import robust_regret

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (Path(__file__).resolve().parents[1] / "config_robustness.json").read_text()
)
CONFIG.update({"interpreter": sys.version.split()[0], "platform": platform.platform()})


def main() -> None:
    rows = []
    t0 = time.perf_counter_ns()
    for d in CONFIG["deltas"]:
        r = robust_regret(CONFIG["payoffs_A"], CONFIG["profile"], CONFIG["profile"], d)
        rows.append(
            {
                "delta_payoff_units": d,
                "nominal_regret": r.nominal_regret,
                "robust_regret": r.robust_regret,
                "worst_deviation": r.worst_deviation,
            }
        )
    elapsed = time.perf_counter_ns() - t0
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    with (out / "payoff-uncertainty.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0])
        w.writeheader()
        w.writerows(rows)
    summary = {
        "config": CONFIG,
        "rows": len(rows),
        "max_bound": max(x["robust_regret"] for x in rows),
        "runtime_ns": elapsed,
        "scope": "exact worst case for independent cellwise box errors; one designed game",
    }
    (out / "payoff-uncertainty.json").write_text(json.dumps(summary, indent=2) + "\n")
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(
        [x["delta_payoff_units"] for x in rows],
        [x["robust_regret"] for x in rows],
        marker="o",
        label="robust regret",
    )
    ax.axhline(0, color="black", lw=0.8)
    ax.set(
        xlabel="Bound δ per payoff cell (utility units)",
        ylabel="Worst-case regret (utility units)",
        title="Payoff uncertainty weakens exact equilibrium certification",
    )
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "payoff-uncertainty.png", dpi=160)
    plt.close(fig)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
