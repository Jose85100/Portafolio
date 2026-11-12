#!/usr/bin/env python3
"""Extract sector-level workplace safety indicators from the official Minsalud workbook."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent
EXPECTED_SHEET = "Din Sector Económico"
FIELDS = [
    "sector", "affiliated_companies", "dependent_affiliations", "independent_affiliations",
    "student_affiliations", "presumed_work_accidents", "work_accidents_occurred",
    "presumed_occupational_disease", "occupational_disease_occurred",
    "deaths_reported_presumed_work_accident", "deaths_reported_presumed_disease",
    "deaths_reported_qualified_work_accident", "deaths_reported_qualified_disease",
    "new_disability_pensions_work_accident", "new_disability_pensions_disease",
    "partial_permanent_disability_work_accident", "partial_permanent_disability_disease",
]
NUMERIC = FIELDS[1:]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def extract(path: Path) -> pd.DataFrame:
    wb = load_workbook(path, read_only=True, data_only=True)
    if EXPECTED_SHEET not in wb.sheetnames:
        raise ValueError(f"Expected sheet missing: {wb.sheetnames}")
    ws = wb[EXPECTED_SHEET]
    title = " ".join(str(row[1]) for row in ws.iter_rows(min_row=5, max_row=6, max_col=2, values_only=True) if row[1])
    if "TRIMESTRE III - AÑO 2026" not in title:
        raise ValueError(f"Unexpected reporting period/title: {title}")
    # Row 25 is the table header. Columns B:R contain sector and 16 numeric metrics.
    table = list(ws.iter_rows(min_row=25, max_col=18, values_only=True))
    rows: list[list[object]] = []
    total = None
    for row in table[1:]:
        sector = row[1]
        if not isinstance(sector, str):
            continue
        values = list(row[1:18])
        if sector.strip().lower() == "total general":
            total = values
        else:
            rows.append(values)
    wb.close()
    df = pd.DataFrame(rows, columns=FIELDS)
    if len(df) != 21 or total is None:
        raise ValueError(f"Expected 21 sectors and a total row; got {len(df)}")
    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if df[NUMERIC].isna().any().any() or (df[NUMERIC] < 0).any().any():
        raise ValueError("Missing, nonnumeric or negative count in source table")
    totals = pd.Series(total[1:], index=NUMERIC, dtype="float64")
    mismatches = {col: [int(df[col].sum()), int(totals[col])] for col in NUMERIC if int(df[col].sum()) != int(totals[col])}
    if mismatches:
        raise ValueError(f"Sector rows do not reconcile to source total: {mismatches}")
    df["affiliation_months"] = df.dependent_affiliations + df.independent_affiliations + df.student_affiliations
    if (df.affiliation_months <= 0).any():
        raise ValueError("Nonpositive affiliation exposure")
    df["accidents_per_10000_affiliation_months"] = 10_000 * df.work_accidents_occurred / df.affiliation_months
    df["qualified_accident_deaths_per_100000_affiliation_months"] = (
        100_000 * df.deaths_reported_qualified_work_accident / df.affiliation_months
    )
    return df


def build(source: Path, out: Path) -> dict:
    df = extract(source)
    out.mkdir(parents=True, exist_ok=True)
    keep = ["sector", *NUMERIC, "affiliation_months", "accidents_per_10000_affiliation_months",
            "qualified_accident_deaths_per_100000_affiliation_months"]
    df[keep].to_csv(out / "sector_safety_indicators_2026q3.csv", index=False, float_format="%.6f")
    plot = df.sort_values("accidents_per_10000_affiliation_months")
    colors = ["#d9822b" if name == "CONSTRUCCION" else "#496d7a" for name in plot.sector]
    fig, ax = plt.subplots(figsize=(12, 8))
    short_labels = {
        "ACTIVIDADES ARTISTICAS, DE ENTRETENIMIENTO Y RECREACION": "Arte y recreación",
        "ACTIVIDADES DE ATENCION DE LA SALUD HUMANA Y DE ASISTENCIA SOCIAL": "Salud y asistencia social",
        "ACTIVIDADES DE LOS HOGARES INDIVIDUALES EN CALIDAD DE EMPLEADORES; ACTIVIDADES NO DIFERENCIADAS DE LOS HOGARES INDIVIDUALES COMO PRODUCTORES DE BIENES Y SERVICIOS PARA USO PROPIO": "Hogares empleadores",
        "ACTIVIDADES DE ORGANIZACIONES Y ENTIDADES EXTRATERRITORIALES ": "Organismos extraterritoriales",
        "ACTIVIDADES DE SERVICIOS ADMINISTRATIVOS Y DE APOYO": "Servicios administrativos",
        "ACTIVIDADES FINANCIERAS Y DE SEGUROS": "Finanzas y seguros",
        "ACTIVIDADES INMOBILIARIAS": "Inmobiliario",
        "ACTIVIDADES PROFESIONALES, CIENTIFICAS Y TECNICAS": "Servicios profesionales",
        "ADMINISTRACION PUBLICA Y DEFENSA; PLANES DE SEGURIDAD SOCIAL DE AFILIACION OBLIGATORIA": "Administración pública",
        "AGRICULTURA, GANADERIA, CAZA, SILVICULTURA Y PESCA": "Agricultura y pesca",
        "ALOJAMIENTO Y SERVICIOS DE COMIDA": "Alojamiento y comida",
        "COMERCIO AL POR MAYOR Y AL POR MENOR; REPARACION DE VEHICULOS AUTOMOTORES Y MOTOCICLETAS": "Comercio y reparación",
        "CONSTRUCCION": "Construcción",
        "DISTRIBUCION DE AGUA; EVACUACION Y TRATAMIENTO DE AGUAS RESIDUALES, GESTION DE DESECHOS Y ACTIVIDADES DE SANEAMIENTO AMBIENTAL": "Agua y saneamiento",
        "EDUCACION": "Educación",
        "EXPLOTACION DE MINAS Y CANTERAS": "Minas y canteras",
        "INDUSTRIAS MANUFACTURERAS": "Manufactura",
        "INFORMACION Y COMUNICACIONES": "Información y comunicaciones",
        "OTRAS ACTIVIDADES DE SERVICIOS": "Otros servicios",
        "SUMINISTRO DE ELECTRICIDAD, GAS, VAPOR Y AIRE ACONDICIONADO": "Electricidad, gas y vapor",
        "TRANSPORTE Y ALMACENAMIENTO": "Transporte y almacenamiento",
    }
    labels = [short_labels[name] for name in plot.sector]
    ax.barh(labels, plot.accidents_per_10000_affiliation_months, color=colors)
    ax.axvline(df.loc[df.sector.eq("CONSTRUCCION"), "accidents_per_10000_affiliation_months"].iloc[0], color="#d9822b", linestyle="--", linewidth=1)
    ax.set(title="Accidentes de trabajo sucedidos por sector · T3 2026",
           xlabel="Por 10.000 afiliaciones-mes (dependientes + independientes + estudiantes)")
    ax.grid(axis="x", alpha=.25)
    fig.text(.01, .005, "Fuente: Minsalud. Agregado sectorial; no representa empresas u obras individuales.", fontsize=8)
    fig.subplots_adjust(left=.31, right=.98, top=.93, bottom=.11)
    fig.savefig(out / "sector_work_accident_rate_2026q3.png", dpi=170, facecolor="white")
    plt.close(fig)
    construction = df.loc[df.sector.eq("CONSTRUCCION")].iloc[0]
    manifest = {
        "provider": "Ministerio de Salud y Protección Social de Colombia",
        "dataset": "Indicadores del Sistema General de Riesgos Laborales por actividad económica y departamento",
        "source_page": "https://minsalud.gov.co/Proteccion-Social/RiesgosLaborales/Paginas/indicadores.aspx",
        "source_file": "estadisticas-sgrl-actividad-economica-depto.zip",
        "source_url": "https://minsalud.gov.co/sites/rid/Lists/BibliotecaDigital/RIDE/VP/RBC/estadisticas-sgrl-actividad-economica-depto.zip",
        "source_workbook": "Trimestre 3_2026_Corte Septiembre_SECTOR ECONOMICO.xlsx",
        "sheet": EXPECTED_SHEET, "reporting_period": "2026-Q3 (July–September)",
        "downloaded_at": "2026-11-11", "source_bytes": source.stat().st_size,
        "source_sha256": sha256(source), "sectors": len(df),
        "license_or_reuse_terms": "Not explicitly stated on the cited Minsalud publication page; verify before redistribution beyond this attributed aggregate companion.",
        "source_note": "The workbook states monthly counts are not cumulative; this cut aggregates the three reporting months. Exposure denominator is the sum of dependent, independent and student affiliations over the same period.",
        "qa": {"source_sector_totals_reconcile": True,
               "construction_affiliations_over_period": int(construction.affiliation_months),
               "construction_work_accidents_occurred": int(construction.work_accidents_occurred),
               "construction_accidents_per_10000_affiliation_months": round(float(construction.accidents_per_10000_affiliation_months), 6),
               "construction_deaths_reported_qualified_work_accident": int(construction.deaths_reported_qualified_work_accident)},
        "limitations": ["This is an aggregate sectoral benchmark for the insured population, not a project- or contractor-level loss measure.",
                        "Affiliations are used as exposure-months, not unique workers; the rate is not annualized.",
                        "Reported accidents and fatalities are not project incident outcomes and cannot be linked to SECOP contracts.",
                        "Only the 2026-Q3 workbook is captured; it is insufficient for trend inference or forecasting.",
                        "Reporting, classification and coverage exclude workers outside the insured system; no causal attribution is made."]
    }
    (out / "source_quality_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Official extracted XLSX; keep the raw workbook outside the repository")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    print(json.dumps(build(args.input, args.output_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
