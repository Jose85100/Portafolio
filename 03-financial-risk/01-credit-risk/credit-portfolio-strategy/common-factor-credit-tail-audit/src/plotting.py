"""Render measured CSV results without rerunning the numerical experiment."""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def render(root: Path) -> None:
    out = root / "results"
    with (out / "summary.csv").open() as f:
        summary = list(csv.DictReader(f))
    with (out / "convergence.csv").open() as f:
        rows = list(csv.DictReader(f))
    for row in summary:
        for key in ["independent_es", "factor_es"]:
            row[key] = float(row[key])
    for row in rows:
        for key in ["nodes", "rho", "es_error_vs_reference"]:
            row[key] = float(row[key])
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    selected = [r for r in summary if r["regime"] == "base"]
    for i, row in enumerate(selected):
        axes[0].bar(
            i - 0.17,
            row["independent_es"],
            0.32,
            color="#3567A8",
            label="Independencia" if i == 0 else None,
        )
        axes[0].bar(
            i + 0.17,
            row["factor_es"],
            0.32,
            color="#C77432",
            label="Factor rho=0.2" if i == 0 else None,
        )
    axes[0].set(
        xticks=[0, 1],
        xticklabels=["Granular", "Concentrada"],
        ylabel="ES99 (unidades de pérdida)",
        title="Mismos pesos/PD; dependencia distinta",
    )
    axes[0].legend()
    for regime, marker in [("base", "o"), ("stress", "s")]:
        selected = [
            r for r in rows if r["case"] == "granular" and r["regime"] == regime
        ]
        axes[1].plot(
            [r["nodes"] for r in selected],
            [abs(r["es_error_vs_reference"]) for r in selected],
            marker=marker,
            label=f"rho={selected[0]['rho']}",
        )
    axes[1].set(
        xscale="log",
        xlabel="Nodos Gauss-Hermite",
        ylabel="|Error ES99 vs GH256|",
        title="Convergencia observada, sin cota certificada",
    )
    axes[1].set_yscale("log")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(out / "audit.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    render(Path(__file__).resolve().parents[1])
