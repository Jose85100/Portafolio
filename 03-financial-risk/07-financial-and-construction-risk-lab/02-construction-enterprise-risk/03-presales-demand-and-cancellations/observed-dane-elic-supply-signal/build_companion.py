#!/usr/bin/env python3
"""Build descriptive municipal supply/licensing indicators from a DANE ELIC snapshot."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parent
SOURCE_URL = "https://www.dane.gov.co/files/operaciones/ELIC/anex-ELIC-SerieTipoBaseMun-ago2026.xlsx"
EXPECTED_SHA256 = "da11bbfcdeafa05c8f16c81c09d351582e20680aef90b4a9e8bd8aa2394e4943"
LATEST = "2026-08"
COVERAGE_CODES = {"77", "88", "302", "1000+"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build(path: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    actual = sha256(path)
    if actual != EXPECTED_SHA256:
        raise SystemExit(f"Snapshot SHA-256 mismatch: expected {EXPECTED_SHA256}, got {actual}")
    workbook = openpyxl.load_workbook(path, data_only=True, read_only=True)
    sheet = workbook["elic"]
    header = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True))
    expected_header = ("año", "mes", "cod_depto", "cod_muni", "obj_tra", "clase_suelo", "modalidad", "destino", "tipo_vivi", "VIS_NVIS", "estrato", "area", "unidades", "licencias", "cobertura")
    if tuple(header) != expected_header:
        raise SystemExit(f"Unexpected ELIC schema: {header!r}")

    month_destination = defaultdict(lambda: [0.0, 0.0, 0.0])
    month_municipality_destination = defaultdict(lambda: [0.0, 0.0, 0.0])
    month_municipality_housing_type = defaultdict(lambda: [0.0, 0.0, 0.0])
    coverage_counts = defaultdict(int)
    latest_coverage_area = defaultdict(float)
    rows_read = 0
    for row in sheet.iter_rows(min_row=2, values_only=True):
        rows_read += 1
        if row[0] is None or row[1] is None:
            continue
        year, month = int(row[0]), int(row[1])
        coverage = str(row[14]).strip()
        if year >= 2026 and month == 8:
            latest_coverage_area[coverage] += float(row[11] or 0)
        if year < 2019 or coverage not in COVERAGE_CODES:
            continue
        period = f"{year:04d}-{month:02d}"
        destination = int(row[7])
        municipality = f"{str(row[2]).zfill(2)}{str(row[3]).zfill(3)}"
        area, units, licenses = (float(row[i] or 0) for i in (11, 12, 13))
        month_destination[(period, destination)][0] += area
        month_destination[(period, destination)][1] += units
        month_destination[(period, destination)][2] += licenses
        month_municipality_destination[(period, municipality, destination)][0] += area
        month_municipality_destination[(period, municipality, destination)][1] += units
        month_municipality_destination[(period, municipality, destination)][2] += licenses
        if destination == 1:
            housing_type = int(row[8] or 0)
            month_municipality_housing_type[(period, municipality, housing_type)][0] += area
            month_municipality_housing_type[(period, municipality, housing_type)][1] += units
            month_municipality_housing_type[(period, municipality, housing_type)][2] += licenses
        coverage_counts[period] += 1

    destination_names = {
        1: "Vivienda", 2: "Industria", 3: "Oficina", 4: "Bodega", 5: "Comercio",
        6: "Alojamiento", 7: "Educación", 8: "Salud-asistencial", 9: "Administración pública",
        10: "Religioso", 11: "Social-recreacional", 12: "Otros",
    }
    monthly = pd.DataFrame([
        {"period": p, "destination_code": d, "destination": destination_names.get(d, f"Código {d}"),
         "approved_area_m2": vals[0], "approved_housing_units": vals[1], "license_count": vals[2]}
        for (p, d), vals in sorted(month_destination.items())
    ])
    muni = pd.DataFrame([
        {"period": p, "municipality_code": code, "destination_code": d,
         "approved_area_m2": vals[0], "approved_housing_units": vals[1], "license_count": vals[2]}
        for (p, code, d), vals in sorted(month_municipality_destination.items())
    ])
    municipality_names = {}
    municipalities_sheet = workbook["lista municipios"]
    for row in municipalities_sheet.iter_rows(min_row=2, values_only=True):
        if row[0] is not None and row[1] is not None:
            municipality_names[f"{str(row[0]).zfill(2)}{str(row[1]).zfill(3)}"] = f"{row[3]}, {row[2]}"
    muni["municipality_name"] = muni["municipality_code"].map(municipality_names)
    if muni["municipality_name"].isna().any():
        raise SystemExit("Unmatched municipality DIVIPOLA codes")
    type_names = {0: "No aplica", 1: "Casas", 2: "Apartamentos"}
    muni_housing_type = pd.DataFrame([
        {"period": p, "municipality_code": code, "housing_type_code": kind,
         "housing_type": type_names.get(kind, f"Código {kind}"), "approved_area_m2": vals[0],
         "approved_housing_units": vals[1], "license_count": vals[2]}
        for (p, code, kind), vals in sorted(month_municipality_housing_type.items())
    ])
    muni_housing_type["municipality_name"] = muni_housing_type["municipality_code"].map(municipality_names)
    if monthly.empty or monthly["period"].max() != LATEST:
        raise SystemExit(f"Expected latest period {LATEST}; found {monthly['period'].max() if not monthly.empty else 'none'}")
    if monthly.duplicated(["period", "destination_code"]).any() or muni.duplicated(["period", "municipality_code", "destination_code"]).any():
        raise SystemExit("Duplicate keys after aggregation")
    if (monthly[["approved_area_m2", "approved_housing_units", "license_count"]] < 0).any().any():
        raise SystemExit("Negative aggregate values found")
    periods = sorted(monthly["period"].unique())
    if periods != pd.period_range("2019-01", "2026-08", freq="M").astype(str).tolist():
        raise SystemExit("Missing month(s) in national coverage period 2019-01 to 2026-08")
    latest = monthly[monthly.period == LATEST]
    area_total = float(latest.approved_area_m2.sum())
    housing_area = float(latest.loc[latest.destination_code == 1, "approved_area_m2"].sum())
    nonhousing_area = area_total - housing_area
    # DANE's 2026-Aug bulletin reports these rounded values; compare at whole m².
    if round(area_total) != 1_322_000 or round(housing_area) != 1_010_109 or round(nonhousing_area) != 311_891:
        raise SystemExit(f"August 2026 does not reconcile to DANE bulletin: total={area_total:.1f}, housing={housing_area:.1f}, nonhousing={nonhousing_area:.1f}; latest-area-by-coverage={dict(latest_coverage_area)}")

    metadata = {
        "source": SOURCE_URL, "sha256": actual, "vintage": "DANE ELIC, August 2026; page updated 2026-10-15",
        "sheet": "elic", "rows_read": rows_read, "period_start": periods[0], "period_end": periods[-1],
        "months": len(periods), "coverage_codes_included": sorted(COVERAGE_CODES),
        "grain_source": "month × municipality DIVIPOLA × trámite × land class × modality × destination × housing type × VIS/NVIS × stratum",
        "derived_grain": "month × destination; month × municipality × destination",
        "filter": "months 2019-01 through 2026-08; aggregate the coverage cohorts 77, 88, 302 and 1000+ into the national total",
        "latest_checks_m2": {"total": round(area_total), "housing": round(housing_area), "nonhousing": round(nonhousing_area), "area_by_coverage_cohort": {k: round(v) for k, v in latest_coverage_area.items()}},
        "note": "Licensing/supply signal only; not sales, presales, cancellations, demand or project-level outcomes."
    }
    return monthly, muni, muni_housing_type, metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-xlsx", required=True, type=Path, help="Official DANE ELIC workbook; keep raw outside this repository")
    args = parser.parse_args()
    monthly, muni, muni_housing_type, metadata = build(args.source_xlsx.expanduser().resolve())
    monthly.to_csv(ROOT / "monthly_by_destination.csv", index=False, float_format="%.1f")
    muni.to_csv(ROOT / "monthly_by_municipality_destination.csv", index=False, float_format="%.1f")
    muni_housing_type.to_csv(ROOT / "monthly_municipality_housing_type.csv", index=False, float_format="%.1f")
    (ROOT / "source_and_qa.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    totals = monthly.groupby("period", as_index=False).agg(approved_area_m2=("approved_area_m2", "sum"))
    housing = monthly[monthly.destination_code == 1].set_index("period")["approved_area_m2"]
    latest_municipalities = muni[(muni.period == LATEST) & (muni.destination_code == 1)].nlargest(12, "approved_area_m2")
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={"height_ratios": [1.2, 1]})
    axes[0].plot(totals.period, totals.approved_area_m2 / 1_000_000, color="#274c77", lw=1.6, label="Total")
    axes[0].plot(housing.index, housing.values / 1_000_000, color="#e07a35", lw=1.4, label="Vivienda")
    axes[0].set_ylabel("Área licenciada (millones de m²)")
    axes[0].set_title("DANE ELIC: actividad licenciada, cobertura nacional (2019–ago 2026)")
    axes[0].grid(axis="y", alpha=.25)
    axes[0].legend(frameon=False)
    axes[1].bar(latest_municipalities.municipality_name, latest_municipalities.approved_area_m2 / 1_000, color="#4c956c")
    axes[1].set_ylabel("Vivienda, miles de m²")
    axes[1].set_title("12 códigos municipales con mayor área de vivienda licenciada en ago 2026")
    axes[1].tick_params(axis="x", rotation=45)
    axes[1].grid(axis="y", alpha=.25)
    fig.text(.01, .005, "Indicador de licenciamiento/oferta formal; no representa ventas, preventas ni cancelaciones.", fontsize=9)
    fig.tight_layout(rect=(0, .025, 1, 1))
    fig.savefig(ROOT / "elic_supply_signal.png", dpi=170)
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
