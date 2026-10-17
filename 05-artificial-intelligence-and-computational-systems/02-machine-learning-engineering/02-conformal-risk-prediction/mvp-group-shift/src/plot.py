from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .report import report

rows = report()
fig, ax = plt.subplots(figsize=(8, 4))
for method in ("global", "group"):
    selected = [r for r in rows if r["method"] == method]
    ax.plot([r["regime"] for r in selected],
            [r["worst_group"] for r in selected], marker="o", label=method)
ax.axhline(.9, color="black", linestyle="--")
ax.set_ylabel("Worst-group coverage")
ax.legend()
fig.tight_layout()
fig.savefig(Path(__file__).resolve().parents[1]/"results/worst_group.svg")
