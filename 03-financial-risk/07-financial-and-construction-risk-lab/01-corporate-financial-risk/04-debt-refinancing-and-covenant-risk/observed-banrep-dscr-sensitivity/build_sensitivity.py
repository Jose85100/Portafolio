#!/usr/bin/env python3
"""Apply observed BanRep commercial loan rates to a hypothetical interest-only debt."""
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
SOURCE = (HERE.parents[1] / "03-credit-spread-and-refinancing-risk" /
          "observed-banrep-commercial-credit-cost" / "data" /
          "banrep_series_15129_monthly.csv")
SOURCE_MANIFEST = SOURCE.parent / "source_manifest.json"
OUT = HERE / "results"
PRINCIPAL_COP = 10_000_000_000
CFADS_COP = 2_000_000_000
DSCR_THRESHOLDS = (1.2, 1.5)


def main():
    source_bytes = SOURCE.read_bytes()
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    rows = list(csv.DictReader(source_bytes.decode("utf-8-sig").splitlines()))
    if not rows or list(rows[0]) != ["period", "effective_annual_rate_pct"]:
        raise SystemExit("Unexpected source schema")
    history = []
    for row in rows:
        rate = float(row["effective_annual_rate_pct"])
        interest = PRINCIPAL_COP * rate / 100
        dscr = CFADS_COP / interest
        history.append({"period": row["period"], "observed_rate_pct": rate,
                        "hypothetical_annual_interest_cop": round(interest, 2),
                        "hypothetical_interest_only_dscr": round(dscr, 6),
                        "below_dscr_1_2": dscr < 1.2, "below_dscr_1_5": dscr < 1.5})
    OUT.mkdir(exist_ok=True)
    with (OUT / "monthly_sensitivity.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(history[0]))
        writer.writeheader(); writer.writerows(history)
    rates = sorted(r["observed_rate_pct"] for r in history)
    latest = history[-1]
    rate_break_even = CFADS_COP / PRINCIPAL_COP * 100
    summary = {
        "source_series": "BanRep 15129, weighted average effective annual rate on commercial preferential/corporate bank lending",
        "source_file": str(SOURCE.relative_to(HERE.parents[2])),
        "source_sha256": source_hash,
        "source_manifest": str(SOURCE_MANIFEST.relative_to(HERE.parents[2])),
        "observations": len(history), "period_start": history[0]["period"],
        "period_end": latest["period"], "latest_observed_rate_pct": latest["observed_rate_pct"],
        "hypothetical_principal_cop": PRINCIPAL_COP, "hypothetical_annual_cfads_cop": CFADS_COP,
        "debt_service_assumption": "interest-only, annualized principal × observed effective annual rate; excludes principal amortization, fees, taxes, spread, and compounding schedule",
        "latest_annual_interest_sensitivity_cop": latest["hypothetical_annual_interest_cop"],
        "latest_dscr_sensitivity": latest["hypothetical_interest_only_dscr"],
        "historical_rate_median_pct": rates[len(rates)//2] if len(rates)%2 else (rates[len(rates)//2-1]+rates[len(rates)//2])/2,
        "historical_rate_p90_pct": rates[round(.9*(len(rates)-1))],
        "break_even_rate_pct_for_dscr_1_2": rate_break_even / 1.2,
        "descriptive_months_below_dscr_threshold": {
            str(t): sum(r["hypothetical_interest_only_dscr"] < t for r in history)
            for t in DSCR_THRESHOLDS
        },
        "interpretation": "Illustrative sensitivity only. Historical rates are not a forecast, issuer quote, covenant observation, or breach probability.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    fig, ax = plt.subplots(figsize=(10, 5.2))
    x = [r["period"] for r in history]
    y = [r["hypothetical_interest_only_dscr"] for r in history]
    ax.plot(x, y, color="#225d78", lw=1.7)
    for threshold in DSCR_THRESHOLDS:
        ax.axhline(threshold, ls="--", lw=1, label=f"Umbral hipotético {threshold:.1f}x")
    tick_idx = list(range(0, len(x), 24))
    ax.set_xticks(tick_idx, [x[i] for i in tick_idx], rotation=45, ha="right")
    ax.set(title="DSCR hipotético frente a tasas comerciales observadas",
           ylabel="CFADS / servicio proxy de intereses (x)", xlabel="Mes")
    ax.legend(frameon=False); ax.grid(alpha=.2); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "dscr_historical_sensitivity.png", dpi=180); plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter([r["observed_rate_pct"] for r in history], y, s=13, alpha=.55, color="#bd632f")
    ax.axhline(1.2, ls="--", color="#555", lw=1)
    ax.set(title="Sensibilidad DSCR al costo observado de crédito comercial",
           xlabel="Tasa efectiva anual observada (%)", ylabel="DSCR hipotético (x)")
    ax.grid(alpha=.2); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "dscr_rate_sensitivity.png", dpi=180); plt.close(fig)
    manifest = {"input_sha256": {str(SOURCE.relative_to(HERE.parents[2])): source_hash},
                "output_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "manifest.json"}}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
