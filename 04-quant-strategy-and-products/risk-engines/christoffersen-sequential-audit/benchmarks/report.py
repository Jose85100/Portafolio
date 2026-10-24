import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "results/run.json").read_text())
rows = data["scenarios"]
with (ROOT / "results/summary.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
labels = [row["name"] for row in rows]
x = range(len(rows))
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].bar([i - 0.18 for i in x], [r["fixed_wrong"] for r in rows], 0.36, label="MC fijo")
axes[0].bar([i + 0.18 for i in x], [r["sequential_wrong"] for r in rows], 0.36, label="Secuencial")
axes[0].set_ylabel("decisiones erróneas / 200")
axes[0].set_xticks(list(x), labels, rotation=20)
axes[0].legend()
axes[1].bar(labels, [r["mean_sequential_draws"] for r in rows])
axes[1].set_ylabel("simulaciones medias")
axes[1].tick_params(axis="x", rotation=20)
fig.tight_layout()
fig.savefig(ROOT / "results/sequential-audit.png", dpi=160)
