"""Execute the C++ oracle, preserve raw results, and render an audit figure."""

import csv
import json
import platform
import resource
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)
completed = subprocess.run(
    [ROOT / "build" / "exact_audit"], check=True, capture_output=True, text=True
)
payload = json.loads(completed.stdout)
payload["environment"] = {
    "platform": platform.platform(),
    "python": platform.python_version(),
    "peak_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
}
(RESULTS / "run.json").write_text(
    json.dumps(payload, indent=2) + "\n", encoding="utf-8"
)
with (RESULTS / "summary.csv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=["method", "p_or_error", "microseconds"])
    writer.writeheader()
    writer.writerow(
        {
            "method": "exact",
            "p_or_error": payload["exact_p"],
            "microseconds": payload["exact_microseconds"],
        }
    )
    writer.writerow(
        {
            "method": "monte_carlo_999",
            "p_or_error": payload["max_abs_mc_error"],
            "microseconds": payload["mc_microseconds_per_seed"],
        }
    )

labels = ["Exacto", "MC: error máximo"]
values = [payload["exact_p"], payload["max_abs_mc_error"]]
fig, axes = plt.subplots(1, 2, figsize=(9, 4.2))
axes[0].bar(labels, values, color=["#2878B5", "#F28E2B"], hatch=["", "//"])
axes[0].axhline(0.05, color="black", linestyle="--", label="umbral 5%")
axes[0].set(
    ylabel="Probabilidad",
    title="P-valor exacto y error MC",
    ylim=(0, max(values) * 1.3),
)
axes[0].legend(frameon=False)
axes[1].bar(
    ["Acuerdo", "Desacuerdo"],
    [
        payload["mc_seeds"] - payload["decision_disagreements"],
        payload["decision_disagreements"],
    ],
    color=["#59A14F", "#E15759"],
    hatch=["", "//"],
)
axes[1].set(ylabel="Semillas", title="Decisión MC frente al oracle")
fig.suptitle("Auditoría exacta de independencia: n=30, cuatro excepciones")
fig.tight_layout()
fig.savefig(RESULTS / "audit.png", dpi=160)
plt.close(fig)
print(json.dumps(payload, indent=2))
