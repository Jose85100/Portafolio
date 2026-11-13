"""Reproduce a nominal 10-year yield-differential proxy from frozen official series."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "official-proxy"
FIG = ROOT / "reports" / "figures"
NS = {"g": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic"}


def parse_tes(path: Path) -> tuple[dict[str, float], dict]:
    raw = path.read_bytes()
    root = ET.fromstring(raw)
    target = None
    for series in root.findall(".//g:Series", NS):
        dimensions = {v.attrib["id"]: v.attrib["value"] for v in series.findall("g:SeriesKey/g:Value", NS)}
        if dimensions.get("SUBJECT") == "IRGBRY10":
            target = (series, dimensions)
            break
    if target is None:
        raise ValueError("BanRep TES extract lacks the 10-year zero-coupon series IRGBRY10")
    series, dimensions = target
    if dimensions.get("REFERENCE_AREA") != "CO" or dimensions.get("UNIT_MEASURE") != "PT" or dimensions.get("FREQ") != "M":
        raise ValueError(f"Unexpected BanRep TES dimensions: {dimensions}")
    values = {}
    for obs in series.findall("g:Obs", NS):
        period = obs.find("g:ObsDimension", NS).attrib["value"]
        raw_value = float(obs.find("g:ObsValue", NS).attrib["value"])
        # BanRep's SDMX payload stores this rate as a fraction; the portal reports percent.
        value = raw_value * 100
        if len(period) != 7 or not math.isfinite(value) or value <= 0 or period in values:
            raise ValueError(f"Invalid or duplicate TES observation: {period}")
        values[period] = value
    if len(values) < 200 or sorted(values) != list(values):
        raise ValueError("Unexpected TES monthly coverage/order")
    meta = {"file": path.name, "sha256": hashlib.sha256(raw).hexdigest(), "raw_bytes": len(raw),
            "dataflow": "DF_TES_MONTHLY_HIST", "series_subject": "IRGBRY10", "unit": "percent",
            "raw_encoding": "fraction; multiplied by 100 for percent", "frequency": "monthly",
            "observations": len(values), "first_month": min(values), "last_month": max(values)}
    return values, meta


def parse_ust(path: Path) -> tuple[dict[str, float], dict]:
    raw = path.read_bytes()
    by_month: dict[str, list[float]] = defaultdict(list)
    daily = 0
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["observation_date", "DGS10"]:
            raise ValueError(f"Unexpected Treasury CSV columns: {reader.fieldnames}")
        seen = set()
        for row in reader:
            day, text = row["observation_date"], row["DGS10"]
            if not text or text == ".":
                continue
            val = float(text)
            if day in seen or not math.isfinite(val) or not 0 < val < 30:
                raise ValueError(f"Invalid or duplicate Treasury observation {day}")
            seen.add(day)
            by_month[day[:7]].append(val)
            daily += 1
    values = {m: sum(v) / len(v) for m, v in by_month.items()}
    meta = {"file": path.name, "sha256": hashlib.sha256(raw).hexdigest(), "raw_bytes": len(raw),
            "series_id": "DGS10", "unit": "percent", "frequency": "daily source; arithmetic monthly mean",
            "nonmissing_daily_observations": daily, "monthly_observations": len(values),
            "first_month": min(values), "last_month": max(values)}
    return values, meta


def main() -> dict:
    tes, tes_meta = parse_tes(RAW / "banrep-tes-zero-coupon-monthly-2003-2026.xml")
    ust, ust_meta = parse_ust(RAW / "fred-us-treasury-10y-dgs10-daily.csv")
    months = sorted(set(tes) & set(ust))
    if not months or months != sorted(months):
        raise ValueError("No valid common month sample")
    # Preserve source gaps: report them explicitly and never interpolate.
    expected = []
    year, month = map(int, months[0].split("-"))
    end_year, end_month = map(int, months[-1].split("-"))
    while (year, month) <= (end_year, end_month):
        expected.append(f"{year:04d}-{month:02d}")
        month += 1
        if month == 13:
            year, month = year + 1, 1
    missing_months = [m for m in expected if m not in months]
    rows = [{"month": m, "colombia_tes_10y_nominal_pct": tes[m], "us_treasury_10y_nominal_pct": ust[m],
             "nominal_yield_differential_proxy_pp": tes[m] - ust[m]} for m in months]
    proxies = [r["nominal_yield_differential_proxy_pp"] for r in rows]
    summary = {"construct": "nominal 10-year government yield differential proxy",
               "formula": "BanRep COP TES zero-coupon 10y yield (%) minus US Treasury constant-maturity 10y yield (%)",
               "unit": "percentage points", "observations": len(rows), "coverage": f"{months[0]} to {months[-1]}",
               "missing_paired_months_not_interpolated": missing_months,
               "sources": [tes_meta, ust_meta],
               "proxy_interpretation": "co-movement benchmark for long-term local-currency sovereign financing conditions relative to a U.S. benchmark; not a pure sovereign default-risk premium",
               "statistics_pp": {"mean": sum(proxies) / len(proxies), "minimum": min(proxies), "maximum": max(proxies),
                                 "latest_month": rows[-1]["month"], "latest": proxies[-1]},
               "assumptions_and_expected_bias": [
                   "Both quoted rates are treated as comparable 10-year nominal government yields; differences in duration construction, liquidity, tax treatment, and market microstructure remain.",
                   "The differential includes expected inflation, expected depreciation and currency-risk compensation, local monetary-policy expectations, term premia, liquidity and credit risk. It will generally overstate or understate default risk depending on these components.",
                   "No hedge is applied. A U.S.-dollar investor's realized currency exposure is not removed, and the spread is not a tradable arbitrage measure.",
                   "Monthly averaging smooths daily volatility and may hide within-month repricing; the BanRep curve estimate is a model-based zero-coupon yield.",
                   "No causal relation to debt, fiscal news, or macro fundamentals is estimated in this companion."],
               "admissible_use": "descriptive monitoring of relative long-term nominal financing conditions and a reproducible proxy input for sensitivity scenarios; not credit-rating, CDS, expected-loss, or investment decision substitute",
               "limitations": ["The sample starts in 2003 because the captured BanRep TES 10-year history begins then.",
                               "No official same-currency matched instrument or direct Colombian sovereign CDS/EMBI series is included.",
                               "The U.S. Treasury yield and TES zero-coupon curve differ in currency, inflation regime, market depth and benchmark construction."]}
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    with (OUT / "monthly_yield_differential.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    (OUT / "proxy_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    try:
        import matplotlib.pyplot as plt
        plt.style.use("seaborn-v0_8-whitegrid")
        fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
        axes[0].plot(months, [r["colombia_tes_10y_nominal_pct"] for r in rows], label="TES cero cupón 10 años (COP)", color="#b91c1c")
        axes[0].plot(months, [r["us_treasury_10y_nominal_pct"] for r in rows], label="Treasury 10 años (USD)", color="#245b72")
        axes[0].set_ylabel("Rendimiento nominal (%)"); axes[0].legend(loc="upper right")
        axes[0].set_title("Rendimientos soberanos a 10 años: niveles nominales")
        plot_values = [next((r["nominal_yield_differential_proxy_pp"] for r in rows if r["month"] == m), float("nan")) for m in expected]
        axes[1].plot(expected, plot_values, color="#167c80", lw=1.5)
        axes[1].axhline(0, color="#64748b", lw=.8)
        axes[1].set(title="Proxy de diferencial nominal Colombia–EE.UU.", ylabel="Puntos porcentuales", xlabel="Mes")
        ticks = list(range(0, len(expected), 24))
        axes[1].set_xticks(ticks, [expected[i] for i in ticks], rotation=45)
        fig.tight_layout(); fig.savefig(FIG / "tes-ust-10y-differential-proxy.png", dpi=170); plt.close(fig)
    except ImportError:
        pass
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


if __name__ == "__main__":
    main()
