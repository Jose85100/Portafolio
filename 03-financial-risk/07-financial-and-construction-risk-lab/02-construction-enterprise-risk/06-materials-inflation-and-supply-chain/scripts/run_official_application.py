#!/usr/bin/env python3
"""Build a reproducible DANE ICOCED material-cost monitoring companion."""
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
SOURCE = ROOT / "data/raw/dane_icoced_sep2026.xlsx"
SOURCE_URL = "https://www.dane.gov.co/files/operaciones/ICOCED/anex-ICOCED-sep2026.xlsx"
SHEET = "Anexo 7.2"
DOMAIN = "Bogotá_Cundinamarca AR"
INPUTS = ["Acero corrugado", "Cemento", "Concreto común"]
MONTHS = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5,
    "Junio": 6, "Julio": 7, "Agosto": 8, "Septiembre": 9,
    "Octubre": 10, "Noviembre": 11, "Diciembre": 12,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Source snapshot missing: {SOURCE}")
    workbook = openpyxl.load_workbook(SOURCE, read_only=True, data_only=True)
    if SHEET not in workbook.sheetnames:
        raise ValueError(f"Expected sheet {SHEET!r} not found")
    sheet = workbook[SHEET]

    # The official annex stores each month in a four-column block:
    # index, monthly change, year-to-date change, and annual change.
    year_starts = []
    for col in range(1, sheet.max_column + 1):
        value = sheet.cell(6, col).value
        if isinstance(value, int) and 2022 <= value <= 2030:
            year_starts.append((value, col))
    month_columns = []
    for i, (year, year_col) in enumerate(year_starts):
        # In the first year the fixed descriptor columns precede January; later
        # years start directly on their January block.
        col = year_col + (5 if year == 2022 else 0)
        end_col = year_starts[i + 1][1] if i + 1 < len(year_starts) else sheet.max_column + 1
        while col + 1 < end_col:
            label = sheet.cell(7, col).value
            if label not in MONTHS:
                break
            month_columns.append((year, MONTHS[label], col, label))
            col += 4
    if len(month_columns) < 40:
        raise ValueError(f"Only {len(month_columns)} month blocks found; layout changed")

    records = []
    duplicate_keys = 0
    seen = set()
    target_rows = 0
    nonnumeric = 0
    for row in sheet.iter_rows(min_row=10, max_row=sheet.max_row, values_only=True):
        if row[1] != DOMAIN or row[2] != "Materiales" or row[3] not in INPUTS:
            continue
        target_rows += 1
        key = (row[1], row[2], row[3])
        if key in seen:
            duplicate_keys += 1
        seen.add(key)
        weight = pd.to_numeric(row[4], errors="coerce")
        for year, month, index_col, month_label in month_columns:
            index_value = pd.to_numeric(row[index_col - 1], errors="coerce")
            monthly_change = pd.to_numeric(row[index_col], errors="coerce")
            if pd.isna(index_value) or pd.isna(monthly_change):
                nonnumeric += 1
                continue
            records.append({
                "period": f"{year}-{month:02d}-01",
                "geographic_domain": DOMAIN,
                "cost_group": "Materiales",
                "input": row[3],
                "weight_pct_2021_base": float(weight),
                "index_dec_2021_100": float(index_value),
                "monthly_change_pct": float(monthly_change),
            })
    source_dimensions = [sheet.max_row, sheet.max_column]
    workbook.close()
    data = pd.DataFrame(records)
    if data.empty:
        raise ValueError("No observations found for the selected domain and inputs")
    data["period"] = pd.to_datetime(data["period"])
    data = data.sort_values(["input", "period"]).reset_index(drop=True)
    duplicate_obs = int(data.duplicated(["geographic_domain", "input", "period"]).sum())

    # Market indicator summary only; it is not an estimate of project cost impact.
    summaries = []
    for name, group in data.groupby("input", sort=False):
        group = group.sort_values("period")
        idx = group["index_dec_2021_100"]
        changes = group["monthly_change_pct"]
        summaries.append({
            "input": name,
            "weight_pct_2021_base": float(group["weight_pct_2021_base"].iloc[0]),
            "n_months": int(len(group)),
            "first_period": group["period"].min().strftime("%Y-%m"),
            "last_period": group["period"].max().strftime("%Y-%m"),
            "first_index": float(idx.iloc[0]),
            "latest_index": float(idx.iloc[-1]),
            "index_change_since_first_pct": float((idx.iloc[-1] / idx.iloc[0] - 1) * 100),
            "monthly_change_mean_pct": float(changes.mean()),
            "monthly_change_std_pct": float(changes.std(ddof=1)),
            "monthly_change_p95_pct": float(changes.quantile(0.95)),
            "largest_monthly_increase_pct": float(changes.max()),
            "largest_monthly_decrease_pct": float(changes.min()),
        })

    output = ROOT / "results"
    figures = ROOT / "figures"
    output.mkdir(exist_ok=True)
    figures.mkdir(exist_ok=True)
    data.to_csv(output / "icoced_material_series_bogota.csv", index=False, float_format="%.6f")
    with (output / "summary.json").open("w", encoding="utf-8") as stream:
        json.dump({"domain": DOMAIN, "source_sheet": SHEET, "summary": summaries}, stream,
                  ensure_ascii=False, indent=2)

    colors = {"Acero corrugado": "#146C94", "Cemento": "#E07A3F", "Concreto común": "#3A7D44"}
    fig, ax = plt.subplots(figsize=(10, 5.6))
    for name, group in data.groupby("input", sort=False):
        group = group.sort_values("period")
        ax.plot(group["period"], group["index_dec_2021_100"], label=name,
                color=colors[name], linewidth=2.2)
    ax.set_title("Costos de insumos seleccionados · Bogotá y Cundinamarca")
    ax.set_ylabel("Índice (diciembre 2021 = 100)")
    ax.set_xlabel("Mes")
    ax.grid(axis="y", alpha=.25)
    ax.legend(frameon=False, ncol=3, loc="upper left")
    fig.text(.01, .01, "Fuente: DANE, ICOCED histórico, Anexo 7.2. Variación de costos; no representa precio de compra ni presupuesto de obra.", fontsize=8)
    fig.tight_layout(rect=(0, .04, 1, 1))
    fig.savefig(figures / "icoced_indices.png", dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5.2))
    for name, group in data.groupby("input", sort=False):
        group = group.sort_values("period")
        rolling = group.set_index("period")["monthly_change_pct"].rolling(12, min_periods=6).std()
        ax.plot(rolling.index, rolling, label=name, color=colors[name], linewidth=2)
    ax.set_title("Volatilidad móvil de 12 meses de la variación mensual")
    ax.set_ylabel("Desviación estándar (puntos porcentuales)")
    ax.set_xlabel("Mes")
    ax.grid(axis="y", alpha=.25)
    ax.legend(frameon=False, ncol=3, loc="upper left")
    fig.text(.01, .01, "La volatilidad resume dispersión histórica; no es probabilidad de sobrecosto ni pronóstico.", fontsize=8)
    fig.tight_layout(rect=(0, .04, 1, 1))
    fig.savefig(figures / "icoced_volatility.png", dpi=170)
    plt.close(fig)

    manifest = {
        "source_url": SOURCE_URL,
        "source_snapshot": str(SOURCE.relative_to(ROOT)),
        "sha256": sha256(SOURCE),
        "source_sheet": SHEET,
        "source_sheet_dimensions": source_dimensions,
        "snapshot_downloaded_from_dane": "2026-11-10",
        "reported_update_in_workbook": "2026-09-30",
        "extraction": {
            "domain": DOMAIN,
            "cost_group": "Materiales",
            "inputs": INPUTS,
            "grain": "input × geographic domain × month",
            "period_start": data["period"].min().strftime("%Y-%m"),
            "period_end": data["period"].max().strftime("%Y-%m"),
            "observations": int(len(data)),
            "expected_observations": int(len(INPUTS) * len(month_columns)),
            "source_rows_for_targets": target_rows,
            "duplicate_series_keys": duplicate_keys,
            "duplicate_observations": duplicate_obs,
            "missing_or_nonnumeric_month_cells_skipped": nonnumeric,
        },
        "transformations": [
            "Read Anexo 7.2 rows for Bogotá_Cundinamarca AR and cost group Materiales.",
            "Select Acero corrugado, Cemento and Concreto común; no weights or data are imputed.",
            "Read each monthly block's published index and monthly percentage change.",
            "Compute sample standard deviation, 95th percentile, extrema, and index change from the first observed month.",
        ],
        "limitations": [
            "ICOCED measures cost variation using a representative basket; it is not a transaction price or a project-specific cost index.",
            "Fixed 2021 weights and the selected inputs may not match a project's bill of quantities, procurement terms, or location.",
            "The results do not estimate budget overrun, lead times, supplier risk, or causal pass-through.",
        ],
    }
    with (output / "manifest.json").open("w", encoding="utf-8") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
    report = [
        "# Lectura oficial ICOCED: insumos materiales en Bogotá y Cundinamarca", "",
        f"**Corte de serie:** {data['period'].min():%Y-%m} a {data['period'].max():%Y-%m}. "
        f"**Grano:** insumo × dominio geográfico × mes. **Observaciones:** {len(data)}.", "",
        "Esta aplicación convierte la serie oficial de costos del DANE en una señal externa para revisar escaladores, cláusulas de reajuste y sensibilidad de presupuestos. No valida una pérdida ni calcula el impacto sobre una obra específica.", "",
        "## Resultados", "",
        "| Insumo | Peso base 2021 (%) | Cambio del índice desde primer mes (%) | Desv. estándar mensual (pp) | P95 mensual (%) | Máximo mensual (%) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in summaries:
        report.append(f"| {item['input']} | {item['weight_pct_2021_base']:.3f} | {item['index_change_since_first_pct']:.2f} | {item['monthly_change_std_pct']:.3f} | {item['monthly_change_p95_pct']:.3f} | {item['largest_monthly_increase_pct']:.3f} |")
    report += [
        "", "## Lectura para decisión", "",
        "Las series permiten identificar insumos con mayor dispersión histórica y orientar una revisión de coberturas, escalación contractual o frecuencia de actualización presupuestal. El uso operativo requiere mapear cantidades y fechas de compra del proyecto a estos índices, y verificar el contrato y la geografía aplicable. Los percentiles históricos son escenarios descriptivos; no deben presentarse como probabilidades futuras.", "",
        "## Calidad, linaje y límites", "",
        f"El snapshot oficial contiene dimensiones {manifest['source_sheet_dimensions'][0]:,} × {manifest['source_sheet_dimensions'][1]:,}; la extracción retuvo {len(data)} filas de la selección. Claves duplicadas en las series: {duplicate_obs}. Celdas mensuales ausentes o no numéricas omitidas: {nonnumeric}. No se imputaron observaciones.", "",
        f"SHA-256 del Excel: `{manifest['sha256']}`. Fuente DANE: {SOURCE_URL}", "",
        "ICOCED reemplazó el ICCV tras el rediseño de 2021 y expresa variaciones de costo con base diciembre de 2021 = 100. El índice no es un nivel de precio, una cotización, ni el costo total de construcción. El basket del DANE, sus ponderaciones y la cobertura geográfica no representan necesariamente un proyecto o empresa.", "",
        "## Figuras", "",
        "![Índices](../figures/icoced_indices.png)", "",
        "![Volatilidad](../figures/icoced_volatility.png)", "",
        "## Reproducción", "",
        "Desde esta carpeta: `python3 scripts/run_official_application.py`. Requiere `openpyxl`, `pandas` y `matplotlib`; usa el snapshot local y genera las series, el manifiesto, resumen y figuras.", "",
    ]
    (output / "official_report.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps({"rows": len(data), "period": [data.period.min().strftime('%Y-%m'), data.period.max().strftime('%Y-%m')], "summary": summaries, "sha256": manifest["sha256"], "quality": manifest["extraction"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
