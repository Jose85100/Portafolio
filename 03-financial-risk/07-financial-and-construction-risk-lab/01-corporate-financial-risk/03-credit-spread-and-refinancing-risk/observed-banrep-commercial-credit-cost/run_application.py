#!/usr/bin/env python3
"""Build an observed-rate refinancing-cost sensitivity from the BanRep snapshot."""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data/banrep_series_15129_monthly.csv"
MANIFEST = ROOT / "data/source_manifest.json"
PRINCIPAL_COP = 10_000_000_000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source_manifest = json.loads(MANIFEST.read_text())
    if sha256(SOURCE) != source_manifest["snapshot_csv_sha256"]:
        raise ValueError("BanRep snapshot SHA-256 mismatch")
    with SOURCE.open(newline="") as f:
        rows = list(csv.DictReader(f))
    periods = [r["period"] for r in rows]
    rates = [float(r["effective_annual_rate_pct"]) for r in rows]
    if len(rows) != source_manifest["observations"] or len(set(periods)) != len(periods):
        raise ValueError("Row-count or duplicate-period QA failed")
    if periods != sorted(periods) or not all(0 < x < 100 for x in rates):
        raise ValueError("Date-order or rate-range QA failed")

    s = sorted(rates)
    p90 = s[round(0.90 * (len(s) - 1))]
    scenario_rates = {
        "latest_observed": rates[-1],
        "historical_median": s[(len(s) - 1) // 2],
        "historical_p90": p90,
        "historical_max": s[-1],
    }
    scenarios = [{
        "scenario": name,
        "annual_effective_rate_pct": round(rate, 4),
        "hypothetical_annual_interest_cop": round(PRINCIPAL_COP * rate / 100),
        "principal_cop": PRINCIPAL_COP,
        "period": periods[-1] if name == "latest_observed" else "historical distribution",
    } for name, rate in scenario_rates.items()]

    out = ROOT / "results"
    figs = ROOT / "figures"
    out.mkdir(exist_ok=True)
    figs.mkdir(exist_ok=True)
    result = {
        "purpose": "Historical context for a hypothetical bank-loan refinancing; not an issuer spread or forecast.",
        "principal_cop": PRINCIPAL_COP,
        "latest_period": periods[-1],
        "latest_rate_pct": rates[-1],
        "observations": len(rows),
        "period_coverage": [periods[0], periods[-1]],
        "scenarios": scenarios,
    }
    result_path = out / "refinancing_scenarios.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")

    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.plot(periods, rates, color="#175c8e", linewidth=1.5, label="BanRep effective annual rate")
    ax.axhline(s[(len(s) - 1) // 2], color="#e19a26", linestyle="--", label="Historical median")
    ax.axhline(p90, color="#b4443d", linestyle=":", label="Historical 90th percentile")
    ax.set(title="Commercial preferential/corporate loan rate: historical context",
           ylabel="Effective annual rate (%)", xlabel="Monthly observation")
    ax.grid(axis="y", alpha=.25)
    ax.legend(frameon=False, ncol=3, fontsize=8)
    ax.tick_params(axis="x", labelrotation=45)
    ax.set_xticks(range(0, len(periods), max(1, len(periods)//12)))
    fig.tight_layout()
    fig.savefig(figs / "banrep_rate_history.png", dpi=160)
    plt.close(fig)

    report = [
        "# Observed-rate refinancing sensitivity", "",
        f"Snapshot: {periods[0]}–{periods[-1]} ({len(rows)} monthly observations).",
        f"Latest benchmark: {rates[-1]:.2f}% effective annual, {periods[-1]}.",
        "", "## Hypothetical annual interest on COP 10 billion", "",
        "| Scenario | Effective annual rate | Annual interest (COP) |",
        "|---|---:|---:|",
    ]
    report += [f"| {x['scenario']} | {x['annual_effective_rate_pct']:.2f}% | {x['hypothetical_annual_interest_cop']:,} |" for x in scenarios]
    report += ["", "This is a simple balance × rate annualized sensitivity, not an amortizing-loan quote, issuer-specific spread, bond yield, forecast, or accounting EIR. The series describes weighted average rates on newly disbursed commercial preferential/corporate bank credit, not the cost of any named borrower.", ""]
    (out / "summary.md").write_text("\n".join(report))
    qa = {
        "built_utc": datetime.now(timezone.utc).isoformat(),
        "snapshot_csv_sha256": sha256(SOURCE),
        "result_sha256": sha256(result_path),
        "rows": len(rows), "unique_periods": len(set(periods)),
        "coverage": [periods[0], periods[-1]],
        "qa": {"row_count_matches_manifest": len(rows) == source_manifest["observations"],
               "periods_unique_and_ascending": periods == sorted(set(periods)),
               "all_rates_between_0_and_100": all(0 < x < 100 for x in rates)},
    }
    (out / "qa_manifest.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
