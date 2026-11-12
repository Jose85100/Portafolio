#!/usr/bin/env python3
"""Extract SFC-reported aggregate delinquency ratios by entity and modality."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openpyxl
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/sfc_calidad_cartera_historico.xlsx"
SOURCE_URL = "https://www.superfinanciera.gov.co/loader.php?idFile=1070109&lFuncion=descargar&lServicio=Tools2&lTipo=descargas"
METHOD_SOURCE = ROOT / "data/raw/sfc_metodologia_calidad_cartera.xls"
METHOD_URL = "https://www.superfinanciera.gov.co/loader.php?idFile=1005086&lFuncion=descargar&lServicio=Tools2&lTipo=descargas"
SHEETS = {
    "ICV Cartera Comercial": "Comercial",
    "ICV Cartera de Consumo": "Consumo",
    "ICV Cartera de Vivienda": "Vivienda",
    "ICV Cartera de Microcrédito": "Microcrédito",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def as_number(value):
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main() -> None:
    wb = openpyxl.load_workbook(SOURCE, read_only=True, data_only=True)
    missing_sheets = sorted(set(SHEETS) - set(wb.sheetnames))
    if missing_sheets:
        raise ValueError(f"Missing expected SFC sheets: {missing_sheets}")

    records = []
    expected_periods = None
    source_rows = {}
    source_blanks = {}
    invalid_values = 0
    for sheet_name, modality in SHEETS.items():
        sheet = wb[sheet_name]
        date_row = next(sheet.iter_rows(min_row=6, max_row=6, values_only=True))
        period_cols = [(col, pd.Timestamp(value)) for col, value in enumerate(date_row, 1)
                       if isinstance(value, (pd.Timestamp,)) or hasattr(value, "year")]
        if expected_periods is None:
            expected_periods = [period for _, period in period_cols]
        elif [period for _, period in period_cols] != expected_periods:
            raise ValueError(f"Period headers differ in {sheet_name}")
        rows_count = 0
        blanks = 0
        for row in sheet.iter_rows(min_row=9, max_row=sheet.max_row, values_only=True):
            entity_name = row[4]
            if not entity_name or not str(entity_name).strip():
                continue
            entity_code = row[3]
            entity_type = row[2]
            fna_flag = row[1]
            rows_count += 1
            for col, period in period_cols:
                ratio = as_number(row[col - 1])
                if ratio is None:
                    blanks += 1
                    continue
                if not 0 <= ratio <= 1:
                    invalid_values += 1
                    continue
                records.append({
                    "period": period,
                    "modality": modality,
                    "entity_type_code": str(entity_type) if entity_type is not None else "",
                    "entity_code": str(entity_code) if entity_code is not None else "",
                    "entity_name": str(entity_name).strip(),
                    "fna_flag": str(fna_flag) if fna_flag is not None else "",
                    "icv_reported_ratio": ratio,
                    "icv_reported_pct": ratio * 100,
                })
        source_rows[modality] = rows_count
        source_blanks[modality] = blanks

    dimensions = {name: [wb[name].max_row, wb[name].max_column] for name in SHEETS}
    wb.close()
    data = pd.DataFrame(records)
    if data.empty:
        raise ValueError("No usable SFC ICV rows extracted")
    data = data.sort_values(["modality", "entity_type_code", "entity_code", "period"]).reset_index(drop=True)
    key_cols = ["modality", "entity_type_code", "entity_code", "period"]
    duplicate_keys = int(data.duplicated(key_cols).sum())
    if duplicate_keys:
        raise ValueError(f"Duplicate entity/modality/month observations: {duplicate_keys}")

    stats = (data.groupby(["modality", "period"])["icv_reported_pct"]
             .agg(n_entities="count", median_pct="median", p25_pct=lambda x: x.quantile(.25),
                  p75_pct=lambda x: x.quantile(.75), p90_pct=lambda x: x.quantile(.90))
             .reset_index())
    out = ROOT / "results"
    figdir = ROOT / "figures"
    out.mkdir(exist_ok=True)
    figdir.mkdir(exist_ok=True)
    data["period"] = data["period"].dt.strftime("%Y-%m-%d")
    stats["period"] = stats["period"].dt.strftime("%Y-%m-%d")
    data.to_csv(out / "sfc_icv_entity_modality_month.csv", index=False, float_format="%.8f")
    stats.to_csv(out / "sfc_icv_modality_distribution.csv", index=False, float_format="%.6f")

    # Compare the distribution across entities; do not create an unweighted "system rate".
    colors = {"Comercial": "#176B87", "Consumo": "#D96B27", "Vivienda": "#5C8A3C", "Microcrédito": "#8055A2"}
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    for ax, modality in zip(axes.flat, SHEETS.values()):
        part = stats[stats.modality == modality].copy()
        dates = pd.to_datetime(part.period)
        ax.plot(dates, part.median_pct, color=colors[modality], lw=1.8, label="Mediana entre entidades")
        ax.fill_between(dates, part.p25_pct, part.p75_pct, color=colors[modality], alpha=.18, label="P25–P75")
        ax.set_title(modality)
        ax.set_ylabel("ICV reportado (%)")
        ax.grid(axis="y", alpha=.25)
        ax.legend(frameon=False, fontsize=8)
    fig.suptitle("Indicador oficial de cartera vencida por modalidad\nDistribución de entidades vigiladas, Colombia", y=.99)
    fig.text(.01, .005, "Fuente: SFC. Percentiles no ponderados; composición de entidades puede cambiar. ICV es un proxy de stock vencido, no PD ni transición.", fontsize=8)
    fig.tight_layout(rect=(0, .03, 1, .94))
    fig.savefig(figdir / "sfc_icv_distribution_by_modality.png", dpi=170)
    plt.close(fig)

    latest_period = data.period.max()
    latest_stats = stats[stats.period == latest_period].sort_values("modality")
    summaries = []
    for modality in SHEETS.values():
        segment = stats[stats.modality == modality].sort_values("period")
        latest = segment.iloc[-1]
        year_ago = pd.Timestamp(latest["period"]) - pd.DateOffset(years=1)
        lag = segment[segment.period == year_ago.strftime("%Y-%m-%d")]
        summaries.append({
            "modality": modality,
            "latest_period": latest["period"],
            "entities_latest": int(latest.n_entities),
            "median_icv_pct_latest": float(latest.median_pct),
            "p25_icv_pct_latest": float(latest.p25_pct),
            "p75_icv_pct_latest": float(latest.p75_pct),
            "median_change_12m_percentage_points": float(latest.median_pct - lag.iloc[0].median_pct) if len(lag) else None,
        })
    manifest = {
        "source_url": SOURCE_URL,
        "source_snapshot": "data/raw/sfc_calidad_cartera_historico.xlsx",
        "sha256": sha256(SOURCE),
        "methodology_source_url": METHOD_URL,
        "methodology_snapshot": "data/raw/sfc_metodologia_calidad_cartera.xls",
        "methodology_sha256": sha256(METHOD_SOURCE),
        "downloaded_on": "2026-11-10",
        "source_cutoff": expected_periods[-1].strftime("%Y-%m-%d"),
        "source_sheets": list(SHEETS),
        "source_sheet_dimensions": dimensions,
        "grain": "entity × modality × month",
        "period_start": expected_periods[0].strftime("%Y-%m-%d"),
        "period_end": expected_periods[-1].strftime("%Y-%m-%d"),
        "observations": int(len(data)),
        "periods_per_sheet": len(expected_periods),
        "source_entity_rows_per_modality": source_rows,
        "blank_cells_omitted_per_modality": source_blanks,
        "duplicate_keys": duplicate_keys,
        "invalid_ratios_outside_zero_one": invalid_values,
        "formula_and_interpretation": {
            "source_indicator": "SFC Indicador de Calidad de Cartera por Vencimiento (ICV)",
            "conceptual_formula": "saldo de cartera vencida y leasing vencido / saldo de cartera bruta y leasing bruto × 100",
            "housing_methodology_note": "SFC methodology defines housing delinquency indicators separately for 1–4 months and >4 months; the historic workbook supplies one ICV series per modality, retained as reported without reclassification.",
            "reported_value": "Ratio as provided in SFC workbook; no local numerator/denominator reconstruction",
            "derived_summaries": "unweighted entity-level median and percentiles per modality and month",
        },
        "limitations": [
            "ICV is an aggregate stock ratio and does not identify borrower default probability (PD), loan transitions, or vintage performance.",
            "Entity-level percentiles are unweighted and can change with reporting population, mergers, entries, and exits.",
            "The historical workbook ends at 2023-12; use as a historical official benchmark, not a current monitoring feed.",
            "Accounting/perimeter and SFC reporting changes can affect comparability; the source file does not provide point-in-time revisions.",
        ],
        "latest_distribution": summaries,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    report = [
        "# Proxy observado de calidad de cartera SFC por modalidad", "",
        f"**Serie fuente:** {manifest['period_start'][:7]}–{manifest['period_end'][:7]} ({len(expected_periods)} cortes mensuales). **Corte final del archivo:** {manifest['source_cutoff']}. **Grano:** entidad × modalidad × mes.", "",
        "El indicador de calidad por vencimiento de la SFC se presenta como una señal de deterioro agregado por modalidad. Puede ayudar a priorizar revisión de segmentos y construir escenarios macro o límites de seguimiento. No es una PD de originación, una etiqueta individual de default ni una matriz de transiciones.", "",
        "## Resultado al último corte", "",
        "| Modalidad | Entidades con dato | Mediana ICV (%) | P25–P75 (%) | Cambio mediana en 12 meses (pp) |",
        "|---|---:|---:|---:|---:|",
    ]
    for s in summaries:
        report.append(f"| {s['modality']} | {s['entities_latest']} | {s['median_icv_pct_latest']:.2f} | {s['p25_icv_pct_latest']:.2f}–{s['p75_icv_pct_latest']:.2f} | {s['median_change_12m_percentage_points']:+.2f} |" if s["median_change_12m_percentage_points"] is not None else f"| {s['modality']} | {s['entities_latest']} | {s['median_icv_pct_latest']:.2f} | {s['p25_icv_pct_latest']:.2f}–{s['p75_icv_pct_latest']:.2f} | n/d |")
    report += [
        "", "## Definición y decisiones metodológicas", "",
        "- **Indicador observado:** ICV mensual por entidad y modalidad, reportado por la SFC. El concepto es saldo vencido dividido por saldo bruto. El runner conserva el cociente publicado; no reconstruye numerador o denominador a partir de alturas de mora superpuestas.",
        "- **Distribución:** mediana y percentiles no ponderados entre entidades por modalidad y mes. No se calcula una tasa de sistema ponderada a partir de ratios entidad, porque no se dispone aquí del denominador bruto alineado para ponderar.",
        "- **Datos faltantes:** se omiten celdas vacías y no se convierten en cero. Ceros numéricos publicados se conservan como cero.",
        "- **Clave:** código de tipo de entidad × código de entidad × modalidad × mes. Cambios de razón social y composición requieren revisar equivalencias antes de comparar una entidad a través del tiempo.",
        "", "## Límites de uso y sesgos", "",
        "El numerador vencido es un saldo de cartera ya deteriorada en una fecha; no es un conteo de nuevos defaults. El ratio mezcla comportamiento, saldo amortizado, castigos, curas, originación, composición y cambios de perímetro. La mediana de entidades da el mismo peso a entidades pequeñas y grandes; por ello describe la institución típica de la muestra y no el sistema agregado. Entradas, salidas, fusiones, cambios de modalidad y coberturas pueden mover la distribución sin un cambio comparable en riesgo subyacente.",
        "La serie histórica incluida termina en diciembre de 2023. No se usa para límites actuales ni calibración de PD/LGD/EAD, scoring, transición, IFRS 9, cosechas o decisiones de crédito. Para eso se requieren microdatos fechados con saldo bruto/vencido, definición de default, observación por operación y seguimiento temporal; además de revisiones de vintage, cobertura y aprobaciones de MRM.",
        "", "## Fuente y calidad", "",
        f"Fuente primaria: [SFC, histórico de calidad de cartera](https://www.superfinanciera.gov.co/publicaciones/10082252/informes-y-cifrascifrasestablecimientos-de-creditoinformacion-periodicamensualcalidad-de-cartera-establecimientos-de-credito-10082252/). Archivo congelado en `{manifest['source_snapshot']}`; SHA-256: `{manifest['sha256']}`.",
        f"Metodología SFC descargada a `{manifest['methodology_snapshot']}`; SHA-256: `{manifest['methodology_sha256']}`. La definición general es cartera y leasing vencidos / cartera y leasing brutos × 100. Para vivienda, la metodología documenta indicadores separados por alturas (1–4 y más de 4 meses); este análisis conserva la serie histórica publicada sin reconstruir ni reasignar esas bandas.",
        f"Extracción: {len(data)} valores numéricos válidos en cuatro modalidades; {duplicate_keys} llaves duplicadas; {invalid_values} ratios fuera de [0,1] omitidos. Celdas vacías omitidas por modalidad: `{json.dumps(source_blanks, ensure_ascii=False)}`. Las hojas del archivo reportan periodicidad mensual y fuente en estados financieros/Formato 0.",
        "", "## Figura", "", "![Distribución de ICV por modalidad](../figures/sfc_icv_distribution_by_modality.png)",
        "", "## Reproducción", "", "Desde esta carpeta: `python3 scripts/build_sfc_quality_proxy.py`. Requiere `openpyxl`, `pandas` y `matplotlib`; toma el snapshot local y regenera CSV, manifiesto, resumen visual e informe.", "",
    ]
    (out / "official_proxy_report.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps({"snapshot_sha256": manifest["sha256"], "period": [manifest["period_start"], manifest["period_end"]], "observations": len(data), "source_rows": source_rows, "blank_cells": source_blanks, "latest": summaries}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
