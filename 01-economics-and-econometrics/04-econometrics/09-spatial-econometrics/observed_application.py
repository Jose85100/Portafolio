#!/usr/bin/env python3
"""Descriptive municipal concentration companion using DANE VAM, 2011–2024p."""

from __future__ import annotations

import csv
import hashlib
import json
import argparse
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parent
EXPECTED_SHA256 = "083bb4b8501db9572867faf7ed71bc5fd9fbd9e269f576dbc1fb2379ade2281d"
MANIFEST = ROOT / "data" / "manifest.json"
REPORT_DIR = ROOT / "reports"
FIGURE = REPORT_DIR / "figures" / "municipal_va_concentration.png"
TABLE = REPORT_DIR / "municipal_va_concentration.csv"
REPORT = REPORT_DIR / "observed_application.md"
DANE_PAGE = "https://www.dane.gov.co/index.php/estadisticas-por-tema/cuentas-nacionales/cuentas-nacionales-departamentales"
N_MUNICIPALITIES = 1123


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def gini(values: np.ndarray) -> float:
    ordered = np.sort(values.astype(float))
    n = len(ordered)
    if n == 0 or ordered.sum() <= 0:
        raise ValueError("Gini requiere observaciones y suma positiva")
    return float(2 * np.dot(np.arange(1, n + 1), ordered) / (n * ordered.sum()) - (n + 1) / n)


def load_series(raw: Path) -> tuple[list[dict], dict]:
    if not raw.is_file():
        raise FileNotFoundError(f"No existe el archivo canónico indicado con --source: {raw}")
    actual_hash = sha256(raw)
    if actual_hash != EXPECTED_SHA256:
        raise ValueError(f"Hash fuente no coincide con manifiesto Atlas: {actual_hash}")

    workbook = load_workbook(raw, read_only=True, data_only=True)
    sheet = workbook["Cuadro 1"]
    headers = next(sheet.iter_rows(min_row=11, max_row=11, values_only=True))
    year_columns: list[tuple[int, str]] = []
    for column, value in enumerate(headers):
        if isinstance(value, int) and 2011 <= value <= 2023:
            year_columns.append((column, str(value)))
        elif value == "2024p":
            year_columns.append((column, "2024p"))
    if len(year_columns) != 14:
        raise ValueError(f"Se esperaban 14 columnas anuales; encontradas {len(year_columns)}")

    records: list[tuple[str, str, str, list[float]]] = []
    for row in sheet.iter_rows(min_row=12, values_only=True):
        code = row[0]
        if not (isinstance(code, str) and code.isdigit() and len(code) == 5):
            continue
        values = [row[col] for col, _ in year_columns]
        if any(not isinstance(value, (int, float)) for value in values):
            raise ValueError(f"Dato anual ausente/no numérico para DIVIPOLA {code}")
        numeric = [float(value) for value in values]
        if any(value < 0 for value in numeric):
            raise ValueError(f"Valor agregado negativo para DIVIPOLA {code}")
        records.append((code, str(row[1]).strip(), str(row[3]).strip(), numeric))
    workbook.close()

    codes = [row[0] for row in records]
    if len(records) != N_MUNICIPALITIES or len(set(codes)) != N_MUNICIPALITIES:
        raise ValueError(f"Grano inesperado: {len(records)} filas, {len(set(codes))} códigos únicos")

    rows: list[dict] = []
    for index, (year_col, year_label) in enumerate(year_columns):
        values = np.array([record[3][index] for record in records], dtype=float)
        total = float(values.sum())
        if total <= 0:
            raise ValueError(f"Suma no positiva en {year_label}")
        top10 = np.partition(values, -10)[-10:]
        rows.append({
            "year": year_label,
            "municipalities": len(values),
            "municipalities_zero_va": int(np.count_nonzero(values == 0)),
            "total_va_cop_billions_current": total,
            "gini_municipal_va": gini(values),
            "top10_municipalities_share": float(top10.sum() / total),
            "top1_municipality_share": float(values.max() / total),
        })

    metadata = {
        "source": "DANE, Cuentas Nacionales Departamentales — Valor agregado por municipio, Base 2015",
        "source_page": DANE_PAGE,
        "drive_file_id": "1JcmDYMPOH60ZElvBvfK5waRnBp3cH6yl",
        "drive_snapshot_modified": "2026-10-08T18:16:04.269Z",
        "snapshot_file": raw.name,
        "snapshot_bytes": raw.stat().st_size,
        "source_path_policy": "Ruta recibida por --source; no se persiste en el manifiesto",
        "snapshot_sha256": actual_hash,
        "workbook_sheet": "Cuadro 1",
        "workbook_grain": "DIVIPOLA municipality × annual period",
        "unit": "COP billions, current prices (precios corrientes), base 2015",
        "coverage": "2011–2023; 2024p shown separately as provisional",
        "municipality_rows": len(records),
        "zero_value_reported_rows": sorted({r[0] for r in records if any(x == 0 for x in r[3])}),
    }
    return rows, metadata


def write_outputs(rows: list[dict], metadata: dict) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with TABLE.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    years = np.arange(2011, 2025)
    top10 = np.array([row["top10_municipalities_share"] for row in rows]) * 100
    gini_values = np.array([row["gini_municipal_va"] for row in rows])
    fig, axes = plt.subplots(2, 1, figsize=(9.5, 6.2), sharex=True, constrained_layout=True)
    for ax, series, title, ylabel in [
        (axes[0], top10, "Participación de los 10 municipios con mayor VA", "% del total nacional"),
        (axes[1], gini_values, "Desigualdad de la distribución municipal del VA", "Coeficiente de Gini"),
    ]:
        ax.plot(years[:-1], series[:-1], color="#145C72", marker="o", linewidth=2)
        ax.plot(years[-2:], series[-2:], color="#B45F06", marker="o", linewidth=2, linestyle="--")
        ax.scatter(years[-1], series[-1], color="#B45F06", marker="D", s=48, zorder=3)
        ax.axvline(2023.5, color="#777777", linewidth=0.8, linestyle=":")
        ax.set_title(title, loc="left", fontsize=11, weight="bold")
        ax.set_ylabel(ylabel)
        ax.grid(axis="y", alpha=0.22)
    axes[1].set_xticks(years)
    axes[1].set_xticklabels([str(y) for y in years[:-1]] + ["2024p"])
    fig.suptitle("Valor agregado municipal DANE · precios corrientes", fontsize=13, weight="bold")
    fig.savefig(FIGURE, dpi=180, bbox_inches="tight")
    plt.close(fig)

    by_year = {row["year"]: row for row in rows}
    y0, y1 = by_year["2011"], by_year["2023"]
    yp = by_year["2024p"]
    delta_top_pp = 100 * (y1["top10_municipalities_share"] - y0["top10_municipalities_share"])
    delta_gini = y1["gini_municipal_va"] - y0["gini_municipal_va"]
    top10_2023 = y1["top10_municipalities_share"] * 100
    report_text = f"""# Aplicación observada: concentración municipal del valor agregado

## Resultado

Entre 2011 y 2023, la participación conjunta de los diez municipios con mayor valor agregado cayó de {y0['top10_municipalities_share']*100:.2f}% a {top10_2023:.2f}% del total nacional ({delta_top_pp:+.2f} puntos porcentuales). El Gini municipal del valor agregado pasó de {y0['gini_municipal_va']:.4f} a {y1['gini_municipal_va']:.4f} ({delta_gini:+.4f}). La distribución sigue muy concentrada: en 2023 los diez mayores municipios reúnen {top10_2023:.1f}% del total.

El dato 2024p se conserva como referencia provisional: top 10 = {yp['top10_municipalities_share']*100:.2f}%; Gini = {yp['gini_municipal_va']:.4f}. No se incluye como cierre del cambio 2011–2023.

![Concentración municipal y Gini, 2011–2024p](figures/municipal_va_concentration.png)

## Método y grano

Se usan los 1.123 códigos DIVIPOLA de cinco dígitos del Cuadro 1, una fila por municipio/unidad territorial publicada, con valor agregado total anual. El corte incluye Nuevo Belén de Bajirá (código 27493) en años previos a su creación con valor cero, según la nota del propio cuadro; también mantiene los ceros reportados para Mapiripana (94663) desde 2020. El Gini se calcula sobre la distribución de niveles, incluidos los ceros reportados: `G = 2 Σ(i·x_(i)) / (n Σx) − (n+1)/n`, con `x` ordenado de menor a mayor. La participación top 10 es la suma de los diez valores municipales mayores dividida por la suma nacional. No se prorratea ni se interpolan observaciones.

El archivo reporta precios corrientes en miles de millones de pesos; por ello las métricas son participaciones/dispersiones dentro de cada año. No deben interpretarse como crecimiento real ni bienestar per cápita. Los ceros que aparecen están preservados y contados como reportados; no se recodifican como datos faltantes.

## Fuente, vintage y reproducción

Fuente primaria: DANE, [Cuentas Nacionales Departamentales]({DANE_PAGE}), archivo “Valor agregado por municipio: serie 2011–2024 provisional”, Base 2015. La [ficha metodológica VAM](https://www.dane.gov.co/files/operaciones/PIB/departamental/DSO-VAM-FME-001-V2.pdf) documenta la operación y el tratamiento provisional/definitivo; el [boletín departamental](https://www.dane.gov.co/files/operaciones/PIB/bol-PIBDep-2023p.pdf) presenta el agregado municipal como una desagregación territorial anual de cuentas departamentales. El dato crudo se lee desde el archivo canónico de Drive indicado al runner, sin copiarse al producto. El SHA-256 esperado del manifiesto del Atlas (corte 2026-10-08) es `{metadata['snapshot_sha256']}`. La actualización publicada por DANE está fechada 3 de julio de 2026. La fuente se lee sin transformación; este runner solo procesa el Cuadro 1 y genera agregados descriptivos.

Requisitos: Python 3, `openpyxl`, `numpy`, `matplotlib`. El archivo fuente debe estar disponible desde la copia canónica/sincronizada de Drive; no forma parte de este repositorio.

```bash
python3 -m pip install openpyxl numpy matplotlib
python3 observed_application.py --source "/ruta/a/Master_DATOS/ATLAS_ECONOMICO_COLOMBIA/01_RAW/dane_valor_agregado_municipal_2011_2024p.xlsx"
```

Salidas: `reports/municipal_va_concentration.csv`, `reports/figures/municipal_va_concentration.png` y `data/manifest.json`. El runner verifica antes de leer que el hash de `--source` sea el esperado, y valida unicidad del código DIVIPOLA, 1.123 filas, cobertura anual, no negatividad y completitud. La ruta local completa no se escribe en el manifiesto.

## Lectura, decisión admisible y límites

El companion permite dimensionar la concentración de actividad económica municipal y priorizar preguntas territoriales, cortes departamentales o requerimientos de desagregación. La reducción de concentración en la métrica top 10 es descriptiva; su magnitud no identifica convergencia de productividad, reasignación causal ni spillovers geográficos. Los montos nominales también mezclan volumen y precios relativos sectoriales.

Este resultado no estima `ρ` en `y = ρWy + Xβ + ε`. No hay matriz espacial `W` en esta entrega. Antes de una especificación espacial se requiere congelar geometría oficial DIVIPOLA con vintage compatible, verificar correspondencia de códigos y ensayar matrices alternativas (contigüidad y distancia), además de definir controles y estrategia de identificación. La unidad estadística es valor agregado territorial estimado en cuentas departamentales; el uso admisible aquí es monitoreo distributivo y diseño de preguntas, no inferencia causal ni asignación de recursos por sí sola.

El laboratorio sintético y su notebook permanecen intactos: continúan siendo el espacio para estudiar dependencia espacial, endogeneidad y desempeño de estimadores bajo un DGP controlado. La aplicación observada comprueba que el insumo económico tiene grano municipal anual y revela el tipo de concentración que un análisis posterior debe explicar.
""".replace("\u200b", "")
    REPORT.write_text(report_text, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="Ruta al XLSX canónico del Atlas en 01_RAW")
    args = parser.parse_args()
    data, meta = load_series(args.source.expanduser())
    write_outputs(data, meta)
    print(f"municipios={meta['municipality_rows']}; sha256={meta['snapshot_sha256']}")
    for year in ("2011", "2023", "2024p"):
        row = next(item for item in data if item["year"] == year)
        print(f"{year}: top10={row['top10_municipalities_share']:.4%}; gini={row['gini_municipal_va']:.4f}; total={row['total_va_cop_billions_current']:.3f}")
