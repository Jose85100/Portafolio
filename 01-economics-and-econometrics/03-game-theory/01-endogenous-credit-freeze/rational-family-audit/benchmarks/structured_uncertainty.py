import csv
import json
import platform
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
from src.epsilon_robustness import robust_regret
from src.uncertainty_structures import shared_opponent_shock_regret

ROOT = Path(__file__).resolve().parents[1]
cfg = json.loads((ROOT / "config_structured_uncertainty.json").read_text())
g = cfg["game"]
A = g["payoffs"]
p = g["own_strategy"]
q = g["opponent_strategy"]
base = robust_regret(A, p, q, 0).robust_regret
rows = []
for d in cfg["deltas"]:
    rows.append(
        {
            "delta": d,
            "nominal_regret": base,
            "shared_state_shock_regret": shared_opponent_shock_regret(A, p, q, d),
            "independent_cell_box_regret": robust_regret(A, p, q, d).robust_regret,
        }
    )
out = ROOT / "results/structured_uncertainty"
out.mkdir(parents=True, exist_ok=True)
with (out / "comparison.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)
(out / "metrics.json").write_text(
    json.dumps(
        {
            "config": cfg,
            "python": sys.version,
            "platform": platform.platform(),
            "rows": rows,
            "conclusion": "shared opponent-state shocks cancel in deviation regret; cellwise independent shocks need not",
        },
        indent=2,
    )
    + "\n"
)
fig, ax = plt.subplots()
ax.plot(
    [r["delta"] for r in rows],
    [r["shared_state_shock_regret"] for r in rows],
    marker="o",
    label="common opponent-state shock",
)
ax.plot(
    [r["delta"] for r in rows],
    [r["independent_cell_box_regret"] for r in rows],
    marker="s",
    label="independent cellwise box",
)
ax.set(
    xlabel="Shock bound δ (payoff units)",
    ylabel="Worst-case regret (payoff units)",
    title="Uncertainty structure changes regret",
)
ax.grid(alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig(out / "comparison.png", dpi=160)
print(json.dumps(rows))
