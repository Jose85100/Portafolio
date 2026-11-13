"""Generate tabular and graphical evidence from the fixed config."""
from __future__ import annotations

import csv
import json
import platform
import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src.robust_regret import factor_loading_regret, nominal_regret, rectangular_cell_regret  # noqa: E402


def main() -> None:
    config: dict[str, Any] = json.loads((ROOT / "config.json").read_text())
    game = config["game"]
    a, p, q = game["payoffs"], game["own_strategy"], game["opponent_strategy"]
    base = nominal_regret(a, p, q)
    rows: list[dict[str, float | str | bool]] = []
    for delta in config["deltas"]:
        for label, lam in config["loadings"].items():
            rows.append({"delta": delta, "structure": label, "regret": factor_loading_regret(a, p, q, lam, delta), "threshold_exceeded": factor_loading_regret(a, p, q, lam, delta) > config["decision_threshold"]})
        rows.append({"delta": delta, "structure": "independent_cell_rectangular", "regret": rectangular_cell_regret(a, p, q, delta), "threshold_exceeded": rectangular_cell_regret(a, p, q, delta) > config["decision_threshold"]})
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    with (out / "comparison.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    hetero = config["loadings"]["heterogeneous"]
    slope = max(abs(x - sum(p[i] * hetero[i] for i in range(2))) for x in hetero) * sum(q)
    cutoff = (config["decision_threshold"] - base) / slope if slope else None
    summary = {
        "nominal_regret": base,
        "heterogeneous_factor_slope": slope,
        "analytic_threshold_delta": cutoff,
        "decision_threshold": config["decision_threshold"],
        "delta_0_2": {str(row["structure"]): row["regret"] for row in rows if row["delta"] == 0.2},
        "data_status": config["data"],
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
        "interpretation": "Synthetic sensitivity only; no empirical inference or equilibrium claim.",
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    structures = ["equal", "heterogeneous", "independent_cell_rectangular"]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    for structure in structures:
        series = [next(float(row["regret"]) for row in rows if row["delta"] == delta and row["structure"] == structure) for delta in config["deltas"]]
        ax.plot(config["deltas"], series, marker="o", label=structure)
    ax.axhline(config["decision_threshold"], color="black", linestyle="--", label="decision threshold")
    ax.set(xlabel="Shock bound δ", ylabel="Worst-case mixed regret", title="Regret under alternative error structures")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "sensitivity.png", dpi=160)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
