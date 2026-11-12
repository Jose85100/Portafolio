#!/usr/bin/env python3
"""Rebuild CEED stage-share proxy from the frozen DANE workbook."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/raw/dane_ceed_structure_area_por_estado_2026q2.xlsx"
SHEET = "Serie 20 áreas (57_mpios)"
DESTINATIONS = {"Apartamentos", "Casas"}
QUARTER = {"I": 1, "II": 2, "III": 3, "IV": 4}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract() -> pd.DataFrame:
    workbook = load_workbook(SNAPSHOT, data_only=True, read_only=True)
    sheet = workbook[SHEET]
    destination = None
    rows = []
    for cells in sheet.iter_rows(min_row=16, values_only=True):
        year, quarter = cells[1], cells[2]
        if cells[0] is not None:
            destination = str(cells[0]).strip()
        if destination not in DESTINATIONS or not isinstance(year, int) or quarter not in QUARTER:
            continue
        total_censused, completed, process_total, paused_total = cells[3], cells[4], cells[8], cells[11]
        values = [total_censused, completed, process_total, paused_total]
        if any(not isinstance(v, (int, float)) for v in values):
            raise ValueError(f"Missing/non-numeric area values at {destination}, {year} Q{quarter}")
        if total_censused <= 0 or min(values) < 0:
            raise ValueError(f"Invalid area values at {destination}, {year} Q{quarter}")
        rows.append({
            "destination": destination,
            "year": year,
            "quarter": QUARTER[quarter],
            "period": f"{year}Q{QUARTER[quarter]}",
            "censused_area_m2": int(total_censused),
            "completed_area_m2": int(completed),
            "in_process_area_m2": int(process_total),
            "paused_inactive_area_m2": int(paused_total),
        })
    workbook.close()
    data = pd.DataFrame(rows)
    expected_periods = pd.period_range("2015Q4", "2026Q2", freq="Q-DEC").astype(str).tolist()
    if len(data) != 86 or data.groupby("destination").size().to_dict() != {"Apartamentos": 43, "Casas": 43}:
        raise ValueError("Expected 43 quarterly observations for each residential destination")
    if any(set(data.loc[data.destination == dest, "period"]) != set(expected_periods) for dest in DESTINATIONS):
        raise ValueError("Missing or unexpected quarterly periods")
    if data.duplicated(["destination", "period"]).any():
        raise ValueError("Duplicate destination-period keys")
    return data.sort_values(["destination", "year", "quarter"]).reset_index(drop=True)


def main() -> None:
    data = extract()
    components = data.groupby("period", as_index=False)[[
        "censused_area_m2", "completed_area_m2", "in_process_area_m2", "paused_inactive_area_m2"
    ]].sum()
    components.insert(1, "destination", "Vivienda (apartamentos + casas)")
    combined = pd.concat([data, components], ignore_index=True).sort_values(["period", "destination"])
    combined["paused_inactive_share_pct"] = 100 * combined.paused_inactive_area_m2 / combined.censused_area_m2
    combined["in_process_share_pct"] = 100 * combined.in_process_area_m2 / combined.censused_area_m2
    combined.to_csv(ROOT / "results/ceed_stage_share_by_quarter.csv", index=False)

    latest = combined[combined.period == "2026Q2"].set_index("destination")
    yoy = combined[combined.period.isin(["2025Q2", "2026Q2"])].pivot(
        index="destination", columns="period", values="paused_inactive_share_pct"
    )
    report_lines = [
        "# Resultado reproducible: proxy de área paralizada/inactiva en CEED",
        "",
        "El anexo describe área física censada en estados de obra; el cociente es un contexto sectorial. No mide atraso contractual, pérdida, mora, inventario no vendido ni desempeño de proyectos individuales.",
        "",
        "## Corte más reciente (2026-T2)",
        "",
        "| Destino | Área censada (m²) | Área paralizada/inactiva (m²) | Proxy sobre área censada (%) | Área en proceso (%) |",
        "|---|---:|---:|---:|---:|",
    ]
    for destination in ["Apartamentos", "Casas", "Vivienda (apartamentos + casas)"]:
        row = latest.loc[destination]
        report_lines.append(
            f"| {destination} | {int(row.censused_area_m2):,} | {int(row.paused_inactive_area_m2):,} | "
            f"{row.paused_inactive_share_pct:.2f} | {row.in_process_share_pct:.2f} |"
        )
    report_lines += ["", "## Comparación interanual del proxy", "", "| Destino | 2025-T2 (%) | 2026-T2 (%) | Cambio (pp) |", "|---|---:|---:|---:|"]
    for destination, row in yoy.iterrows():
        report_lines.append(f"| {destination} | {row['2025Q2']:.2f} | {row['2026Q2']:.2f} | {row['2026Q2']-row['2025Q2']:+.2f} |")
    report_lines += [
        "",
        "## Interpretación",
        "",
        "`Área paralizada o inactiva / área total censada` aproxima la fracción del área observada que DANE clasifica en ese estado. Puede activar revisión sectorial de exposición a obras detenidas y orientar escenarios de seguimiento; no se interpreta como tasa de incumplimiento ni como riesgo causal. El área total censada es el denominador explícito. Para vivienda, se suman metros cuadrados de apartamentos y casas antes de dividir; no se promedian porcentajes.",
        "",
        "La población geográfica corresponde a la cobertura agregada del anexo Serie 20 áreas (57 municipios), que agrupa 14 áreas urbanas, cinco metropolitanas y Cundinamarca. No es una serie nacional de todos los proyectos ni se desagrega por empresa. El censo distingue obras culminadas, en proceso y paralizadas/inactivas; cambios de cobertura, clasificación y composición pueden mover el cociente.",
        "",
        "Las observaciones de 2026 están dentro de la ventana de provisionalidad que DANE describe como de un año. El snapshot fue publicado el 14 de agosto de 2026. Los resultados pueden revisarse.",
        "",
        "## Reproducción y linaje",
        "",
        "Fuente: [DANE, Censo de Edificaciones, histórico](https://www.dane.gov.co/index.php/comunicados-y-boletines/construccion-y-vivienda/censo-de-edificaciones), archivo `anex-CEED-EstructuraSeriesDestino-IItrim2026.xlsx`, hoja `Serie 20 áreas (57_mpios)`, corte 1997–2026-T2. La edición extrae solo apartamentos y casas desde 2015-T4 hasta 2026-T2.",
        "",
        "- 86 filas destino-trimestre (43 por destino), sin claves duplicadas ni valores de área faltantes en la selección.",
        "- CSV incluye apartados por destino y una agregación reproducible de vivienda (apartamentos + casas), con shares de área en proceso y paralizada/inactiva.",
        f"- SHA-256 snapshot: `{sha256(SNAPSHOT)}`.",
        "- Ejecutar desde esta carpeta: `python3 scripts/build_companion.py` (requiere `openpyxl`, `pandas`, `matplotlib`).",
        "",
        "## Brecha de validación",
        "",
        "Para validar atraso contractual o pérdidas hace falta una muestra interna por obra con fechas planificadas y reales, presupuestos y cambios de alcance, hitos, financiación, preventas/ventas, costos incurridos y resultado final. El CEED solo permite comparar señal sectorial agregada; no calibra parámetros del modelo de sobrecosto/cronograma ni demuestra que la cuota de área paralizada anticipe incumplimientos.",
    ]
    (ROOT / "results/official_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "source": "DANE CEED",
        "source_url": "https://www.dane.gov.co/files/operaciones/CEED/anex-CEED-EstructuraSeriesDestino-IItrim2026.xlsx",
        "source_index": "https://www.dane.gov.co/index.php/comunicados-y-boletines/construccion-y-vivienda/censo-de-edificaciones",
        "snapshot": str(SNAPSHOT.relative_to(ROOT)),
        "sha256": sha256(SNAPSHOT),
        "sheet": SHEET,
        "reported_coverage": "14 áreas urbanas, cinco metropolitanas y Cundinamarca; agregado de Serie 20 áreas (57 municipios)",
        "periods": ["2015Q4", "2026Q2"],
        "destinations": ["Apartamentos", "Casas"],
        "source_grain": "trimestre × destino residencial, área (m²) agregada; no project/company ID",
        "formula": "100 × área paralizada o inactiva al corte / área total censada al corte",
        "observation_count": len(data),
        "observation_count_with_derived_residential_aggregate": len(combined),
        "missing_area_values": 0,
        "duplicate_destination_period_keys": 0,
        "publication_date": "2026-08-14",
        "revision_note": "DANE indica que la provisionalidad se maneja a un año; cortes 2026 dentro de esa ventana.",
        "limitations": [
            "Proxy de composición de área censada, no atraso contractual, default, pérdida, ventas o unidades no vendidas.",
            "La cobertura geográfica es la agregación del anexo de 57 municipios; no cubre todo el universo nacional ni identifica proyectos.",
            "Composición y clasificación de obras pueden variar; últimos cortes sujetos a revisión.",
            "No estima causalidad ni valida el motor de sobrecostos/cronograma.",
        ],
    }
    (ROOT / "results/manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    palette = {"Apartamentos": "#1B6B8A", "Casas": "#D06A3B", "Vivienda (apartamentos + casas)": "#394B59"}
    fig, ax = plt.subplots(figsize=(11, 5.4))
    for destination, group in combined.groupby("destination", sort=False):
        group = group.sort_values("period")
        quarters = pd.PeriodIndex(group.period, freq="Q-DEC").to_timestamp(how="end")
        ax.plot(quarters, group.paused_inactive_share_pct, label=destination, color=palette[destination], lw=1.8)
    ax.axvspan(pd.Timestamp("2025-07-01"), pd.Timestamp("2026-12-31"), color="#8C8C8C", alpha=0.10,
               label="Cortes dentro de ventana de revisión (último año)")
    ax.set_title("Área paralizada/inactiva como proporción del área censada")
    ax.set_ylabel("Porcentaje del área censada (%)")
    ax.set_xlabel("Trimestre (57 municipios; agregado DANE)")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(ROOT / "figures/paused_inactive_area_share.png", dpi=180)
    plt.close(fig)
    print(json.dumps({
        "snapshot_sha256": manifest["sha256"],
        "observations": manifest["observation_count"],
        "periods": manifest["periods"],
        "latest_residential_proxy_pct": float(latest.loc["Vivienda (apartamentos + casas)", "paused_inactive_share_pct"]),
        "latest_residential_in_process_pct": float(latest.loc["Vivienda (apartamentos + casas)", "in_process_share_pct"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
