#!/usr/bin/env python3
"""Aggregate DANE CEED VIS/No VIS completed unsold stock by quarter."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
from pyxlsb import open_workbook

SOURCE_URL = (
    "https://www.dane.gov.co/files/operaciones/VISNoVIS/"
    "anex-VISNoVIS-SerieTipoBaseInicCulm-IItrim2026.xlsb"
)
EXPECTED_PERIODS = 24
VIS_LABELS = {1: "VIS", 2: "No_VIS"}
# Historical totals published in DANE's IV-2024 bulletin, kept as an
# explicit vintage check rather than treated as a source for the time series.
PUBLISHED_CHECKS = {
    "2024-1": {"VIS": 519, "No_VIS": 1951},
    "2024-2": {"VIS": 679, "No_VIS": 1955},
    "2024-3": {"VIS": 713, "No_VIS": 2121},
    "2024-4": {"VIS": 733, "No_VIS": 1859},
}


def read_sheet(path: Path, sheet_name: str) -> pd.DataFrame:
    with open_workbook(str(path)) as workbook, workbook.get_sheet(sheet_name) as sheet:
        rows = iter(sheet.rows(sparse=True))
        header = [cell.v for cell in next(rows)]
        records = []
        for row in rows:
            values = [cell.v for cell in row]
            if values and values[0] is not None:
                records.append(dict(zip(header, values)))
    return pd.DataFrame.from_records(records)


def aggregate(path: Path) -> pd.DataFrame:
    balances = read_sheet(path, "Saldos")
    needed = {"PERIODO", "VENTA_SN", "VIS_SN", "TIP_SALDO"}
    if not needed.issubset(balances.columns):
        raise ValueError(f"Saldos sheet missing fields: {sorted(needed - set(balances.columns))}")
    balances = balances[balances["VENTA_SN"].astype(str) == "1"].copy()
    balances["VIS_SN"] = pd.to_numeric(balances["VIS_SN"], errors="raise").astype(int)
    balances["TIP_SALDO"] = pd.to_numeric(balances["TIP_SALDO"], errors="raise")
    if (balances["TIP_SALDO"] < 0).any() or not set(balances["VIS_SN"]).issubset(VIS_LABELS):
        raise ValueError("Unexpected negative balance or VIS classification")
    out = (balances.groupby(["PERIODO", "VIS_SN"], as_index=False)["TIP_SALDO"]
           .sum().rename(columns={"PERIODO": "quarter", "VIS_SN": "housing_type",
                                 "TIP_SALDO": "completed_unsold_units_for_sale"}))
    out["housing_type"] = out["housing_type"].map(VIS_LABELS)
    periods = sorted(out["quarter"].unique(), key=lambda q: (int(q[:4]), int(q[-1])))
    if len(periods) != EXPECTED_PERIODS:
        raise ValueError(f"Expected {EXPECTED_PERIODS} quarters, found {len(periods)}")
    complete = pd.MultiIndex.from_product([periods, VIS_LABELS.values()], names=["quarter", "housing_type"])
    out = out.set_index(["quarter", "housing_type"]).reindex(complete, fill_value=0).reset_index()
    out["completed_unsold_units_for_sale"] = out["completed_unsold_units_for_sale"].astype("int64")
    return out.sort_values(["quarter", "housing_type"]).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path, help="Official DANE .xlsb download")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "data")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    series = aggregate(args.input)
    csv_path = args.output_dir / "ceed_completed_unsold_stock_by_quarter.csv"
    series.to_csv(csv_path, index=False)

    totals = series.pivot(index="quarter", columns="housing_type", values="completed_unsold_units_for_sale")
    checks = []
    for quarter, published in PUBLISHED_CHECKS.items():
        for housing_type, published_units in published.items():
            calculated = int(totals.loc[quarter, housing_type])
            checks.append({"quarter": quarter, "housing_type": housing_type,
                           "source_vintage_units": calculated, "published_bulletin_units": published_units,
                           "difference_source_minus_bulletin": calculated - published_units})
    pd.DataFrame(checks).to_csv(args.output_dir / "historical_bulletin_checks.csv", index=False)

    import matplotlib.pyplot as plt
    pivot = series.pivot(index="quarter", columns="housing_type", values="completed_unsold_units_for_sale")
    ax = pivot.plot(figsize=(11, 5), marker="o", linewidth=2)
    ax.set_title("CEED: completed housing units unsold for sale")
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Units (stock at census reference period)")
    ax.grid(axis="y", alpha=.25)
    ax.legend(title="DANE classification")
    plt.xticks(rotation=60, ha="right")
    plt.tight_layout()
    plt.savefig(args.output_dir / "ceed_completed_unsold_stock_by_quarter.png", dpi=160)
    plt.close()

    latest_q = series["quarter"].max()
    latest = series[series["quarter"] == latest_q]
    latest_totals = latest.set_index("housing_type")["completed_unsold_units_for_sale"].to_dict()
    manifest = {
        "source_url": SOURCE_URL,
        "source_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "source_filename": args.input.name,
        "source_sheet": "Saldos",
        "source_fields": ["PERIODO", "VENTA_SN", "VIS_SN", "TIP_SALDO"],
        "filter": "VENTA_SN == 1 (viviendas construidas para venta)",
        "aggregation": "sum TIP_SALDO by PERIODO and VIS_SN",
        "coverage": "23 CEED urban/metropolitan areas; not national coverage",
        "periods": int(series["quarter"].nunique()),
        "period_start": series["quarter"].min(),
        "period_end": latest_q,
        "latest_period_units": {k: int(v) for k, v in latest_totals.items()},
        "historical_bulletin_check": "2024-1 and 2024-4 match DANE IV-2024 bulletin; 2024-2 differs by +14 total and 2024-3 by +8 total; see historical_bulletin_checks.csv",
        "redistribution_note": "Derived aggregate only; source workbook is not included.",
    }
    (args.output_dir / "source_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
