"""CLI that runs the audit and persists raw, tabular, and graphical evidence."""

from __future__ import annotations

import json
import platform
import resource
from dataclasses import asdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .experiment import ExperimentConfig, run_experiment

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def main() -> None:
    config_data = json.loads((ROOT / "benchmarks" / "config.json").read_text(encoding="utf-8"))
    config = ExperimentConfig(**config_data)
    trials, summary, metadata = run_experiment(config)
    RESULTS.mkdir(exist_ok=True)
    trials.to_csv(RESULTS / "trials.csv", index=False)
    summary.to_csv(RESULTS / "summary.csv", index=False)

    methods = ["asymptotic", "permutation", "randomized"]
    x = np.arange(len(methods))
    width = 0.36
    null = summary.loc[summary.scenario == "iid_null"].iloc[0]
    alternative = summary.loc[summary.scenario == "markov_clustered"].iloc[0]
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.bar(x - width / 2, [null[f"rejection_{m}"] for m in methods], width, label="IID (tamaño)")
    ax.bar(
        x + width / 2,
        [alternative[f"rejection_{m}"] for m in methods],
        width,
        label="Markov (potencia)",
        hatch="//",
    )
    ax.axhline(config.alpha, color="black", linestyle="--", linewidth=1.2, label="5% nominal")
    ax.set(
        xticks=x,
        xticklabels=["χ² asintótico", "Permutación", "Perm. aleatorizada"],
        ylabel="Frecuencia de rechazo",
        title="Calibración finita de la independencia de excepciones VaR",
        ylim=(0.0, 1.0),
    )
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(RESULTS / "calibration.png", dpi=160)
    plt.close(fig)

    payload = {
        "config": asdict(config),
        "metadata": {
            **metadata,
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        },
        "summary": summary.to_dict(orient="records"),
    }
    (RESULTS / "run.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
