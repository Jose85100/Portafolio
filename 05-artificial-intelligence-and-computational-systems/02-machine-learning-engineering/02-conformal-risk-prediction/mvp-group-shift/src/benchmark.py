import csv
from pathlib import Path
import numpy as np
from .case import case

REGIMES = ("stable", "mixture_shift", "conditional_shift", "rare_group")

def run(output=None):
    rows = []
    for regime in REGIMES:
        for seed in range(30):
            error, groups, global_q, per_group = case(seed, regime)
            for method in ("global", "group"):
                q = np.full(len(groups), global_q) if method == "global" else np.array([per_group.get(int(g), global_q) for g in groups])
                hit = abs(error) <= q
                rows.append((regime, seed, method, float(np.mean(hit)),
                             float(min(np.mean(hit[groups == 0]), np.mean(hit[groups == 1]))),
                             float(np.mean(2*q))))
    path = Path(output or Path(__file__).resolve().parents[1] / "results/raw.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(("regime","seed","method","coverage","worst_group","width"))
        writer.writerows(rows)
    return rows
