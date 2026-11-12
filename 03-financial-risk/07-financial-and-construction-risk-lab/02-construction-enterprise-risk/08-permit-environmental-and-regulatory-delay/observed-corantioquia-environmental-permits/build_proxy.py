#!/usr/bin/env python3
"""Build a privacy-minimized snapshot of Corantioquia environmental-license records."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
FIELDS = ("municipio", "tipo_proyecto", "estado", "expedientes")
EXPECTED_ROWS = 679
EXPECTED_TOTAL = 1790


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build(source: Path, out: Path) -> dict:
    rows = json.loads(source.read_text(encoding="utf-8"))
    df = pd.DataFrame(rows)
    if len(df) != EXPECTED_ROWS or not set(FIELDS).issubset(df.columns):
        raise ValueError(f"Unexpected snapshot shape/schema: rows={len(df)}, columns={list(df.columns)}")
    df = df[list(FIELDS)].copy()
    df["expedientes"] = pd.to_numeric(df.expedientes, errors="coerce")
    if df.expedientes.isna().any() or df.expedientes.le(0).any():
        raise ValueError("Invalid record counts")
    if int(df.expedientes.sum()) != EXPECTED_TOTAL:
        raise ValueError(f"Unexpected total: {df.expedientes.sum()}")
    if not set(df.estado.dropna().unique()).issubset({"Activo", "Archivado"}):
        raise ValueError("Unexpected expediente status value")
    # Only project types explicitly labelled as construction are selected. Material extraction remains in mining.
    construction = df[df.tipo_proyecto.fillna("").str.lower().str.startswith(("construcción", "construc"))].copy()
    if int(construction.expedientes.sum()) != 317 or construction.tipo_proyecto.nunique() != 13:
        raise ValueError("Construction category selection changed; review before updating the scope")
    out.mkdir(parents=True, exist_ok=True)
    all_types = df.groupby(["tipo_proyecto", "estado"], dropna=False, as_index=False).expedientes.sum()
    all_types.to_csv(out / "all_environmental_license_categories_by_status.csv", index=False)
    by_type = construction.groupby(["tipo_proyecto", "estado"], as_index=False).expedientes.sum()
    by_type.to_csv(out / "construction_license_categories_by_status.csv", index=False)
    by_muni = construction.groupby(["municipio", "estado"], dropna=False, as_index=False).expedientes.sum()
    by_muni.to_csv(out / "construction_license_counts_by_municipality.csv", index=False)

    totals = construction.groupby("tipo_proyecto").expedientes.sum().sort_values(ascending=True).tail(10)
    selected = construction[construction.tipo_proyecto.isin(totals.index)]
    pivot = selected.pivot_table(index="tipo_proyecto", columns="estado", values="expedientes", aggfunc="sum", fill_value=0)
    pivot = pivot.loc[totals.index]
    short_labels = {
        "Construcción de carreteras, en la red vial secundaria y terciaria": "Carreteras secundarias/terciarias",
        "Construcción y operación de rellenos sanitarios": "Rellenos sanitarios",
        "Construcción y Operación de Centrales Generadoras": "Centrales generadoras",
        "Construc y operación de C. generadoras con capacidad mayor o igual a 10 MW y menor de 100 MW": "Centrales generadoras 10–100 MW",
        "Construcción de nuevas calzadas, en la red vial secundaria y terciaria": "Nuevas calzadas secundarias/terciarias",
        "Construcción y operación de instalaciones cuyo objeto sea el almacenamiento, tratamiento, aprovechamiento, recuperación y/o disposición final de residuos o desechos peligrosos": "Manejo de residuos peligrosos",
        "Construcción de vías férreas regionales y variantes de estas": "Vías férreas regionales",
        "Construcción y operación de sistemas de tratamiento de aguas residuales que sirvan a poblaciones iguales o superiores a 200.000 habitantes": "Tratamiento de aguas residuales",
        "Construcción y operación de aeropuertos del nivel nacional y de nuevas pistas en los mismos": "Aeropuertos y pistas",
        "Construcción presas, represas o embalses cualquiera sea su destinación con capacidad igual o inferior a 200 millones de m3 de agua": "Presas, represas y embalses",
        "Construcción de rompeolas, tajamares, canales y rellenos hidráulicos": "Obras hidráulicas",
        "Construcción y operación de distritos de riego y/o drenaje para áreas mayores o iguales a 5.000 hectáreas e inferiores o iguales a 20.000 hectáreas": "Distritos de riego/drenaje",
        "Construcción de túneles con sus accesos, en la red vial secundaria y terciaria": "Túneles viales secundarios/terciarios",
    }
    pivot.index = [short_labels[name] for name in pivot.index]
    ax = pivot.plot(kind="barh", stacked=True, figsize=(11, 7), color={"Activo": "#d9822b", "Archivado": "#496d7a"})
    ax.set(title="Expedientes de licenciamiento ambiental con tipo de proyecto de construcción",
           xlabel="Expedientes registrados en snapshot", ylabel="Categoría reportada por Corantioquia")
    ax.grid(axis="x", alpha=.25)
    ax.legend(frameon=False, title="Estado del expediente")
    ax.figure.text(.01, .005, "Corte transversal; estado activo/archivado no mide aprobación, duración ni incumplimiento.", fontsize=8)
    ax.figure.tight_layout(rect=(0, .03, 1, 1))
    ax.figure.savefig(out / "construction_environmental_license_categories.png", dpi=170, facecolor="white")
    plt.close(ax.figure)

    construction_status = construction.groupby("estado").expedientes.sum().to_dict()
    manifest = {
        "provider": "Corporación Autónoma Regional del Centro de Antioquia (Corantioquia)",
        "dataset": "Licencias ambientales en la jurisdicción de Corantioquia", "dataset_id": "h6gr-4izn",
        "dataset_page": "https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Licencias-ambientales-en-la-jurisdicci-n-de-Corant/h6gr-4izn",
        "api_snapshot_query": "https://www.datos.gov.co/resource/h6gr-4izn.json?$select=municipio,tipo_proyecto,estado,count(*)%20as%20expedientes&$group=municipio,tipo_proyecto,estado&$limit=50000",
        "snapshot_date": "2026-11-11", "source_rows": len(df), "source_aggregated_records": int(df.expedientes.sum()),
        "source_fields": sorted(FIELDS), "source_sha256": sha256(source), "source_bytes": source.stat().st_size,
        "output_excludes_expediente_nature_and_company_type": True,
        "construction_category_rule": "tipo_proyecto starts with 'Construcción' or 'Construc'; mineral extraction for construction materials is excluded as mining.",
        "construction_scope": {"aggregated_records": int(construction.expedientes.sum()),
                               "project_categories": int(construction.tipo_proyecto.nunique()),
                               "municipalities": int(construction.municipio.nunique()),
                               "records_by_expediente_status": {k: int(v) for k, v in construction_status.items()}},
        "limitations": ["Snapshot has no application, decision, issuance or closure dates; no permit lead time or regulatory delay can be estimated.",
                        "Active/archived are expediente statuses, not approval/rejection, legal compliance, project delivery or environmental outcomes.",
                        "The dataset covers Corantioquia's jurisdiction only and is not a national census of environmental permits.",
                        "Project-type categories are regulatory labels; they do not confirm that every expediente reached construction or was executed.",
                        "No individual expediente, applicant name or company type is retained in outputs; no link to SECOP or works is available.",
                        "License/reuse terms are not explicitly stated in the catalog metadata; confirm before redistribution beyond attributed aggregate outputs."]
    }
    (out / "source_quality_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "source_municipality_type_status_snapshot.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    result = build(args.input, args.output_dir)
    print(json.dumps(result["construction_scope"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
