"""Reproduce the seeded attribution experiment and raw artifacts."""
from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any

from src.es_attribution import attribute_es

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results"


def main() -> None:
    config = json.loads((ROOT / "benchmarks/config.json").read_text())
    rng = random.Random(config["seed"])
    n = int(config["scenarios"])
    rows: list[list[float]] = []
    raw: list[dict[str, Any]] = []
    # Synthetic P&L components: a shared crisis state creates dependence and
    # asymmetry; magnitudes are intentionally dimensionless proxy units.
    for i in range(n):
        z = [rng.gauss(0.0, 1.0) for _ in range(3)]
        crisis = rng.random() < 0.025
        shock = rng.gauss(0.0, 1.0) if crisis else 0.0
        row = [0.8 * z[0] + 7.0 * shock,
               1.1 * (0.55 * z[0] + 0.84 * z[1]) + 5.0 * shock,
               1.4 * (-0.2 * z[0] + 0.98 * z[2]) + 4.0 * shock]
        rows.append(row)
        raw.append({"scenario": i, "synthetic_crisis": crisis,
                    "COP_FX_loss_proxy": row[0], "TES_RATE_loss_proxy": row[1],
                    "EQUITY_loss_proxy": row[2], "portfolio_loss_proxy": sum(row)})
    alpha = float(config["alpha"])
    attribution = attribute_es(rows, alpha=alpha)
    standalone = [attribute_es([[row[j]] for row in rows], alpha=alpha).es for j in range(3)]
    stand_total = sum(standalone)
    pro_rata = [attribution.es * x / stand_total for x in standalone]
    no_tail = [sum(row[j] for row in rows) / n for j in range(3)]
    # Adverse ablation: delete the crisis regime, changing the distribution.
    noncrisis = [row for row, rec in zip(rows, raw) if not rec["synthetic_crisis"]]
    no_crisis = attribute_es(noncrisis, alpha=alpha)
    OUT.mkdir(exist_ok=True)
    with (OUT / "scenarios.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(raw[0]))
        writer.writeheader(); writer.writerows(raw)
    result = {
        "classification": {"scenario_data": "synthetic", "market_proxy": False,
                           "empirical": False, "units": "dimensionless illustrative loss units"},
        "seed": config["seed"], "n": n, "alpha": alpha, "var": attribution.var,
        "es": attribution.es, "contributions": dict(zip(config["components"], attribution.contributions)),
        "tail_weight_sum": sum(attribution.tail_weights),
        "baseline_standalone_es_prorata": dict(zip(config["components"], pro_rata)),
        "baseline_uniform_mean_contributions": dict(zip(config["components"], no_tail)),
        "adverse_ablation_without_crisis": {"n": len(noncrisis), "var": no_crisis.var,
                                           "es": no_crisis.es,
                                           "contributions": dict(zip(config["components"], no_crisis.contributions))},
        "reconciliation_error": sum(attribution.contributions) - attribution.es,
    }
    (OUT / "metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    with (OUT / "comparison.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["component", "euler_es", "standalone_es_prorata", "mean_loss_uniform"])
        for i, name in enumerate(config["components"]):
            w.writerow([name, attribution.contributions[i], pro_rata[i], no_tail[i]])
    with (OUT / "sensitivity.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["dimension", "setting", "n", "VaR", "ES", "interpretation"])
        for level in (.90, .95, .975, .99):
            a = attribute_es(rows, alpha=level)
            w.writerow(["confidence", level, n, a.var, a.es, "same synthetic sample"])
        for multiplier in (0.0, .5, 1.0, 1.5):
            scaled = [[x * (multiplier if rec["synthetic_crisis"] else 1.0) for x in row]
                      for row, rec in zip(rows, raw)]
            a = attribute_es(scaled, alpha=alpha)
            w.writerow(["crisis_loss_multiplier", multiplier, n, a.var, a.es,
                        "counterfactual shock magnitude; not forecast"])
    try:
        import matplotlib.pyplot as plt
        labels = config["components"]
        x = range(len(labels)); width = .26
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.bar([i-width for i in x], attribution.contributions, width, label="ES Euler de cola")
        ax.bar(x, pro_rata, width, label="Prorrata de ES standalone")
        ax.bar([i+width for i in x], no_tail, width, label="Ablación: media no ponderada")
        ax.set_xticks(list(x), labels); ax.set_ylabel("Pérdida proxy (unidades sintéticas)")
        ax.set_title("Atribución exacta vs. baselines (no datos de mercado)")
        ax.legend(); fig.tight_layout(); fig.savefig(OUT / "attribution.png", dpi=150); plt.close(fig)
    except ImportError:
        (OUT / "figure-unavailable.txt").write_text("Instale matplotlib para reproducir la figura.\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
