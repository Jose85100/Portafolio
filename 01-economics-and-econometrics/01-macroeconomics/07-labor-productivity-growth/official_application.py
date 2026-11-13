"""Reproduce an observed-data productivity companion from a frozen official WDI response."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "official"
FIG = ROOT / "reports" / "figures"
DATA_FILE = "wdi-colombia-gdp-per-person-employed.json"
META_FILE = "wdi-indicator-metadata.json"
INDICATOR = "SL.GDP.PCAP.EM.KD"


def read_source() -> tuple[dict[int, float], dict]:
    path = RAW / DATA_FILE
    raw = path.read_bytes()
    payload = json.loads(raw)
    if len(payload) != 2 or payload[1] is None or payload[0].get("lastupdated") != "2026-10-08":
        raise ValueError("Unexpected WDI response shape or vintage")
    values = {}
    for row in payload[1]:
        if row.get("countryiso3code") != "COL" or row.get("indicator", {}).get("id") != INDICATOR:
            raise ValueError("Unexpected country or indicator")
        year = int(row["date"])
        value = row.get("value")
        if value is None:
            continue
        value = float(value)
        if not math.isfinite(value) or value <= 0 or year in values:
            raise ValueError(f"Invalid or duplicate observation for {year}")
        values[year] = value
    if len(values) != 35 or (min(values), max(values)) != (1991, 2025):
        raise ValueError(f"Unexpected nonmissing coverage: {min(values)}–{max(values)}, n={len(values)}")
    if set(values) != set(range(min(values), max(values) + 1)):
        raise ValueError("Nonmissing annual series has gaps")
    meta_path = RAW / META_FILE
    metadata_raw = meta_path.read_bytes()
    metadata = json.loads(metadata_raw)[1][0]
    if metadata.get("id") != INDICATOR or metadata.get("source", {}).get("id") != "2":
        raise ValueError("Unexpected WDI indicator metadata")
    manifest = {"file": path.name, "sha256": hashlib.sha256(raw).hexdigest(), "raw_bytes": len(raw),
                "response_rows": len(payload[1]), "nonmissing_observations": len(values),
                "first_year": min(values), "last_year": max(values), "last_updated": payload[0]["lastupdated"],
                "metadata_file": meta_path.name, "metadata_sha256": hashlib.sha256(metadata_raw).hexdigest(),
                "indicator_name": metadata["name"], "source_organization": metadata["sourceOrganization"]}
    return values, manifest


def cagr(values: dict[int, float], start: int, end: int) -> float:
    return 100 * (math.exp(math.log(values[end] / values[start]) / (end - start)) - 1)


def main() -> dict:
    values, manifest = read_source()
    rows = []
    base = values[min(values)]
    for year in sorted(values):
        level = values[year]
        row = {"year": year, "gdp_per_person_employed_constant_2021_ppp_usd": level,
               "index_1991_100": 100 * level / base}
        if year - 1 in values:
            row["annual_log_growth_pct"] = 100 * math.log(level / values[year - 1])
            row["annual_percent_change"] = 100 * (level / values[year - 1] - 1)
        else:
            row["annual_log_growth_pct"] = ""
            row["annual_percent_change"] = ""
        rows.append(row)
    summary = {"source": "World Bank World Development Indicators API, Colombia",
               "vintage": "last updated 2026-10-08", "indicator": INDICATOR,
               "indicator_definition": "GDP divided by total employment, expressed in constant 2021 international dollars (PPP)",
               "source_manifest": manifest, "observations": len(values), "coverage": f"{min(values)}–{max(values)}",
               "growth_measure": "100*ln(level_t/level_(t-1))",
               "period_cagr_pct": {"1991-2025": cagr(values, 1991, 2025),
                                   "2010-2019": cagr(values, 2010, 2019),
                                   "2020-2025": cagr(values, 2020, 2025)},
               "level_change_pct_1991_2025": 100 * (values[2025] / values[1991] - 1),
               "interpretation": "observed growth in GDP per employed person; not a total-factor-productivity estimate or causal effect",
               "limitations": ["WDI labels the indicator as staff estimates based on external databases from ILO, UN Population Division, Eurostat, OECD and World Bank",
                               "output per employed person combines capital deepening, worker composition, hours worked, sector shifts, utilization and measurement effects; it is not TFP",
                               "annual frequency and revised source inputs limit real-time use; the historical WDI vintage is not a point-in-time panel",
                               "this single-country series describes realized outcomes but cannot identify the effect of AI, policy or any other intervention"]}
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    with (OUT / "annual_productivity.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    (OUT / "application_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    try:
        import matplotlib.pyplot as plt
        plt.style.use("seaborn-v0_8-whitegrid")
        fig, ax = plt.subplots(figsize=(9.5, 4.8))
        ax.plot([r["year"] for r in rows], [r["index_1991_100"] for r in rows], color="#245b72", lw=2)
        ax.set(title="PIB por persona empleada en Colombia (1991 = 100)", xlabel="Año", ylabel="Índice")
        fig.tight_layout(); fig.savefig(FIG / "wdi-productivity-level-index.png", dpi=170); plt.close(fig)
        growth = [r for r in rows if r["annual_log_growth_pct"] != ""]
        fig, ax = plt.subplots(figsize=(9.5, 4.8))
        colors = ["#b91c1c" if float(r["annual_log_growth_pct"]) < 0 else "#167c80" for r in growth]
        ax.bar([r["year"] for r in growth], [r["annual_log_growth_pct"] for r in growth], color=colors)
        ax.axhline(0, color="#334155", lw=.8)
        ax.set(title="Crecimiento anual del PIB por persona empleada", xlabel="Año", ylabel="Cambio log anual (%)")
        fig.tight_layout(); fig.savefig(FIG / "wdi-productivity-annual-growth.png", dpi=170); plt.close(fig)
    except ImportError:
        pass
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


if __name__ == "__main__":
    main()
