#!/usr/bin/env python3
"""Aggregate UNGRD 2025 emergency reports for hydro-geological event context.

This produces a municipal reporting/impact inventory, not property exposure,
hazard probability, insured loss, or project risk.
"""
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
EXPECTED_SHA256 = "287df83aa1b05e1a80324b200ff4445f8dc240d2a80d65f725ab6b8e01d291ed"
EXPECTED_BYTES = 6_565_780
EXPECTED_ROWS = 6_506
EVENT_GROUPS = {
    "INUNDACION": "Inundación",
    "CRECIENTE SUBITA": "Creciente súbita",
    "AVENIDA TORRENCIAL": "Avenida torrencial",
    "MOVIMIENTO EN MASA": "Movimiento en masa",
}
METRICS = {
    "muertos": "fatalidades_reportadas", "heridos": "heridos_reportados",
    "desapa": "desaparecidos_reportados", "personas": "personas_afectadas_reportadas",
    "familias": "familias_afectadas_reportadas", "viv_destru": "viviendas_destruidas_reportadas",
    "viv_aver": "viviendas_averiadas_reportadas", "vias": "vias_afectadas_reportadas",
    "ptes_vehic": "puentes_vehiculares_afectados_reportados", "ptes_peat": "puentes_peatonales_afectados_reportados",
    "hectareas": "hectareas_afectadas_reportadas",
}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build(source_path: Path, out_dir: Path) -> dict:
    digest = file_sha256(source_path)
    if source_path.stat().st_size != EXPECTED_BYTES or digest != EXPECTED_SHA256:
        raise ValueError(f"Snapshot mismatch: bytes={source_path.stat().st_size}, sha256={digest}")
    data = pd.read_csv(source_path, dtype=str)
    required = {"fecha", "departamento", "municipio", "evento", "codificaci_n_segun_divipola",
                "coordenadas", "codigo_emergencia", *METRICS.keys()}
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError(f"Required columns missing: {missing}")
    if len(data) != EXPECTED_ROWS:
        raise ValueError(f"Unexpected row count: {len(data)}")
    data["fecha"] = pd.to_datetime(data.fecha, errors="coerce")
    if data.fecha.isna().any() or data.fecha.dt.year.nunique() != 1 or int(data.fecha.dt.year.iloc[0]) != 2025:
        raise ValueError("This snapshot is expected to cover calendar year 2025 only")
    if data.duplicated().any():
        raise ValueError(f"Exact duplicate rows found: {int(data.duplicated().sum())}")
    for col in METRICS:
        data[col] = pd.to_numeric(data[col], errors="coerce")
        if data[col].isna().any() or data[col].lt(0).any():
            raise ValueError(f"Null/non-numeric or negative reported impact in {col}")
    data["reported_code"] = data.codificaci_n_segun_divipola.astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    code_format_ok = data.reported_code.str.fullmatch(r"\d{5}").fillna(False)
    zero_coord = data.coordenadas.fillna("").str.strip().isin({"", "0", "0.0"})
    data["event_group"] = data.evento.map(EVENT_GROUPS)
    relevant = data.loc[data.event_group.notna()].copy()
    if relevant.empty:
        raise ValueError("No hydro-geological event rows found")

    out_dir.mkdir(parents=True, exist_ok=True)
    type_summary = relevant.groupby("event_group", as_index=False, sort=False).agg(
        report_rows=("codigo_emergencia", "size"))
    muni_summary = relevant.groupby(["departamento", "municipio", "event_group"], as_index=False, sort=True).agg(
        report_rows=("codigo_emergencia", "size"))
    type_summary.to_csv(out_dir / "event_type_summary_2025.csv", index=False, float_format="%.3f")
    muni_summary.to_csv(out_dir / "municipality_event_summary_2025.csv", index=False, float_format="%.3f")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    ordered = type_summary.sort_values("report_rows")
    axes[0].barh(ordered.event_group, ordered.report_rows, color="#376b80")
    axes[0].set(title="Reportes UNGRD por tipo (2025)", xlabel="Filas reportadas")
    axes[0].grid(axis="x", alpha=.25)
    top = muni_summary.groupby(["departamento", "municipio", "event_group"], as_index=False).report_rows.sum()
    top["place"] = top.municipio + " · " + top.departamento
    top_places = top.groupby("place").report_rows.sum().nlargest(12).index
    pivot = top[top.place.isin(top_places)].pivot(index="place", columns="event_group", values="report_rows").fillna(0)
    pivot = pivot.loc[pivot.sum(axis=1).sort_values().index]
    pivot.plot(kind="barh", stacked=True, ax=axes[1], colormap="viridis")
    axes[1].set(title="12 municipios con más filas reportadas (2025)", xlabel="Filas, no eventos únicos", ylabel="")
    axes[1].grid(axis="x", alpha=.25)
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("UNGRD: inventario municipal de emergencias hidro-geológicas · Colombia, 2025")
    fig.text(.01, .005, "Filas del registro UNGRD; no equivalen a eventos únicos, frecuencia de amenaza ni pérdida asegurada.", fontsize=9)
    fig.tight_layout(rect=(0, .03, 1, .95))
    fig.savefig(out_dir / "ungrd_hydro_geological_events_2025.png", dpi=170, facecolor="white")
    plt.close(fig)

    pair_code_counts = data.groupby(["departamento", "municipio"]).reported_code.nunique()
    normalized = {"rows": len(data), "duplicate_full_rows": int(data.duplicated().sum()),
                  "date_min": data.fecha.min().date().isoformat(), "date_max": data.fecha.max().date().isoformat(),
                  "all_records_year": 2025, "event_types": data.evento.nunique(),
                  "relevant_event_rows": len(relevant),
                  "relevant_event_rows_by_type": {str(k): int(v) for k, v in type_summary.set_index("event_group").report_rows.to_dict().items()},
                  "coordinates_zero_or_blank_rows": int(zero_coord.sum()),
                  "coordinates_nonzero_rows": int((~zero_coord).sum()),
                  "department_municipality_pairs": int(len(pair_code_counts)),
                  "reported_divipola_distinct_values": int(data.reported_code.nunique()),
                  "reported_divipola_non_5_digit_rows": int((~code_format_ok).sum()),
                  "department_municipality_pairs_with_multiple_reported_codes": int(pair_code_counts.gt(1).sum()),
                  "max_reported_codes_for_one_department_municipality_pair": int(pair_code_counts.max()),
                  "relevant_municipality_event_groups": int(len(muni_summary)),
                  "unique_emergency_codes": int(data.codigo_emergencia.nunique()),
                  "duplicate_emergency_codes": int(data.codigo_emergencia.duplicated().sum()),
                  "duplicate_date_place_type_combinations": int(data.duplicated(["fecha", "departamento", "municipio", "evento"]).sum())}
    manifest = {
        "provider": "Unidad Nacional para la Gestión del Riesgo de Desastres (UNGRD)",
        "dataset": "Emergencias UNGRD V2", "dataset_id": "2343-nuqp",
        "dataset_page": "https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Emergencias-UNGRD-V2/2343-nuqp",
        "api_csv": "https://www.datos.gov.co/resource/2343-nuqp.csv?$limit=20000",
        "metadata_api": "https://www.datos.gov.co/api/views/2343-nuqp.json",
        "downloaded_at": "2026-11-11", "source_update_date": "2026-09-22",
        "source_bytes": source_path.stat().st_size, "source_sha256": digest,
        "source_columns": len(pd.read_csv(source_path, nrows=0).columns), "qa": normalized,
        "event_group_mapping": EVENT_GROUPS,
        "outputs_exclude_free_text": True, "reported_impact_fields_aggregated": False,
        "scope": "Municipality/name-level report-row inventory in 2025; not unique event counts, property-level exposure, hazard probability, insured loss, or causal attribution.",
        "limitations": ["The dataset version V2 describes the 2025 annual report and future vintages; this snapshot contains 2025 only.",
                        "The source says it has 61 columns; the API returned 61 columns and 6506 rows, while the portal's rounded row indicator was 13K at access time.",
                        "Coordinates are zero/blank on 6504 of 6506 records; the field labelled DIVIPOLA is internally inconsistent and is not used as a geographic key.",
                        "One emergency code is repeated and date/place/type combinations recur; updates or distinct same-day incidents cannot be separated because there is no stable incident key.",
                        "The script does not sum affected people, dwellings, roads, or hectares because repeated report updates could double-count cumulative impact.",
                        "Reported impact fields are present but not treated as project-level or insured losses.",
                        "No exposures, building locations, construction attributes, or insurance payouts are linked."]
    }
    (out_dir / "source_quality_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Official UNGRD V2 CSV snapshot; keep raw outside the repository")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "official" / "ungrd-2025")
    args = parser.parse_args()
    result = build(args.input.expanduser().resolve(), args.output_dir)
    print(json.dumps(result["qa"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
