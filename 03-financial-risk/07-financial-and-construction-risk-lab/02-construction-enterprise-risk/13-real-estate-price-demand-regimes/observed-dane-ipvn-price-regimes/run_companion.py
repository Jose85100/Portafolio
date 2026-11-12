#!/usr/bin/env python3
"""Extract a descriptive price-growth companion from DANE's IPVN workbook."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openpyxl
import pandas as pd


EXPECTED_SHA256 = "acde19eaf0108b0046c0df926c5047194cb7c2145177f3de45d5738d6fd4b3db"
SOURCE_URL = "https://www.dane.gov.co/files/operaciones/IPVN/anex-IPVN-IItrim2026.xlsx"
ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def extract(path: Path) -> pd.DataFrame:
    actual = sha256(path)
    if actual != EXPECTED_SHA256:
        raise SystemExit(f"Snapshot SHA-256 mismatch: expected {EXPECTED_SHA256}, got {actual}")
    sheet = openpyxl.load_workbook(path, data_only=True, read_only=True)["TOTAL Y DESTINOS "]
    records = []
    year = None
    for row in sheet.iter_rows(min_row=11, values_only=True):
        year_value, quarter = row[0], row[1]
        if isinstance(year_value, (int, float)) and not isinstance(year_value, bool):
            year = int(year_value)
        if year is None or quarter is None:
            continue
        q = str(quarter).strip().upper()
        if q not in {"I", "II", "III", "IV"}:
            continue
        # A1 quarterly variation: total, apartments, houses.
        values = row[2:5]
        if any(v is None for v in values):
            continue
        records.append({
            "period": f"{year}Q{['I', 'II', 'III', 'IV'].index(q) + 1}",
            "year": year,
            "quarter": ['I', 'II', 'III', 'IV'].index(q) + 1,
            "quarterly_change_total_pct": float(values[0]),
            "quarterly_change_apartments_pct": float(values[1]),
            "quarterly_change_houses_pct": float(values[2]),
        })
    df = pd.DataFrame(records)
    if df.empty or df.iloc[-1]["period"] != "2026Q2":
        raise SystemExit(f"Expected latest observation 2026Q2, got {df.iloc[-1]['period'] if len(df) else 'none'}")
    if df["period"].duplicated().any():
        raise SystemExit("Duplicate quarterly observations in source")
    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-xlsx", required=True, type=Path, help="DANE workbook; raw file is kept outside this companion")
    args = parser.parse_args()
    source = args.source_xlsx.expanduser().resolve()
    data = extract(source)
    out_csv = ROOT / "ipvn_quarterly_derived.csv"
    data.to_csv(out_csv, index=False, float_format="%.2f")

    total = data["quarterly_change_total_pct"]
    reference = data[data["period"] <= "2019Q4"]["quarterly_change_total_pct"]
    evaluation = data[data["period"] >= "2020Q1"]
    threshold = float(reference.quantile(0.75))
    latest = data.iloc[-1]
    summary = {
        "source_url": SOURCE_URL,
        "source_sha256": sha256(source),
        "source_vintage": "DANE IPVN, 2026-II release",
        "period_start": str(data.iloc[0]["period"]),
        "period_end": str(latest["period"]),
        "n_quarters": int(len(data)),
        "unit": "quarter-over-quarter percentage variation (%)",
        "descriptive_high_growth_threshold_total_pct": round(threshold, 4),
        "threshold_reference_period": "2004Q1-2019Q4",
        "threshold_reference_n": int(len(reference)),
        "evaluation_period": "2020Q1-2026Q2",
        "evaluation_n": int(len(evaluation)),
        "latest_total_pct": round(float(latest["quarterly_change_total_pct"]), 4),
        "latest_apartments_pct": round(float(latest["quarterly_change_apartments_pct"]), 4),
        "latest_houses_pct": round(float(latest["quarterly_change_houses_pct"]), 4),
        "latest_above_historical_q75": bool(float(latest["quarterly_change_total_pct"]) > threshold),
        "latest_classification": "Post-2019 total quarterly change strictly above the 2004Q1-2019Q4 75th percentile; descriptive flag, not a fitted or predictive regime.",
    }
    (ROOT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    fig, ax = plt.subplots(figsize=(11, 5.5))
    x = range(len(data))
    ax.plot(x, total, color="#1c4966", linewidth=1.35, label="Total IPVN")
    ax.axhline(threshold, color="#c46525", linestyle="--", linewidth=1.2, label=f"P75 referencia 2004-I–2019-IV: {threshold:.2f}%")
    eval_start = int(data.index[data["period"] == "2020Q1"][0])
    eval_x = list(range(eval_start, len(data)))
    eval_y = total.iloc[eval_start:]
    ax.fill_between(eval_x, threshold, eval_y, where=(eval_y > threshold), color="#e8a06c", alpha=0.45, interpolate=True, label="2020-I en adelante sobre P75")
    tick_idx = list(range(0, len(data), 12))
    if len(data) - 1 not in tick_idx:
        tick_idx.append(len(data) - 1)
    ax.set_xticks(tick_idx, [data.iloc[i]["period"] for i in tick_idx], rotation=45, ha="right")
    ax.set_ylabel("Variación trimestral (%)")
    ax.set_title("DANE IPVN: variación trimestral y umbral descriptivo de crecimiento alto")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(ROOT / "ipvn_price_regimes.png", dpi=170)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
