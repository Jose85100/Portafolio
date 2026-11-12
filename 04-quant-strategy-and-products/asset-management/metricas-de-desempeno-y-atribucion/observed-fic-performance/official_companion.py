#!/usr/bin/env python3
"""Build descriptive FIC market-money annual-return series from SFC snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


HERE = Path(__file__).resolve().parent
REFERENCE_PATH = HERE / "data" / "source_reference.json"
REPORTS = HERE / "reports"
REQUIRED_COLUMNS = {
    "fecha_corte",
    "nombre_tipo_entidad",
    "nombre_subtipo_patrimonio",
    "valor_fondos",
    "inversionistas",
    "rent_anual_por_valor",
    "rent_mensual_por_valor",
    "aportes",
    "retiros",
    "registros",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_source(source_path: Path, reference: dict) -> pd.DataFrame:
    actual_hash = sha256_file(source_path)
    if actual_hash != reference["sha256"]:
        raise ValueError(
            f"SHA-256 no coincide: esperado {reference['sha256']}, recibido {actual_hash}"
        )

    data = pd.read_csv(source_path)
    missing_columns = REQUIRED_COLUMNS - set(data.columns)
    if missing_columns:
        raise ValueError(f"Faltan columnas requeridas: {sorted(missing_columns)}")
    if len(data) != reference["rows"]:
        raise ValueError(f"Filas inesperadas: {len(data)} != {reference['rows']}")

    date = pd.to_datetime(data["fecha_corte"], errors="coerce")
    if date.isna().any():
        raise ValueError("Hay fechas vacías o inválidas")
    data["fecha_corte"] = date

    numeric_columns = REQUIRED_COLUMNS - {
        "fecha_corte",
        "nombre_tipo_entidad",
        "nombre_subtipo_patrimonio",
    }
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")
        if data[column].isna().any() or not data[column].map(pd.notna).all():
            raise ValueError(f"Valores vacíos o no numéricos en {column}")
        if not data[column].map(lambda value: abs(value) != float("inf")).all():
            raise ValueError(f"Valores no finitos en {column}")

    string_columns = ["nombre_tipo_entidad", "nombre_subtipo_patrimonio"]
    if data[string_columns].isna().any().any() or data[string_columns].eq("").any().any():
        raise ValueError("Hay etiquetas de entidad o subtipo vacías")

    key = ["fecha_corte", "nombre_tipo_entidad", "nombre_subtipo_patrimonio"]
    if data.duplicated(key).any():
        raise ValueError("La llave fecha × entidad × subtipo no es única")
    if str(data["fecha_corte"].min().date()) != reference["first_observation"]:
        raise ValueError("La fecha inicial no coincide con el snapshot registrado")
    if str(data["fecha_corte"].max().date()) != reference["latest_observation"]:
        raise ValueError("La fecha final no coincide con el snapshot registrado")
    return data


def build_series(data: pd.DataFrame, reference: dict) -> pd.DataFrame:
    selection = reference["selection"]
    selected = data.loc[
        data["nombre_tipo_entidad"].eq(selection["entity_type"])
        & data["nombre_subtipo_patrimonio"].eq(selection["subtype"])
    ].copy()
    if selected.empty:
        raise ValueError("No hay observaciones para la selección definida")
    if (selected["valor_fondos"] <= 0).any():
        raise ValueError("El valor agregado del fondo debe ser positivo")

    # La consulta fuente sumó rentabilidad × valor del fondo; dividir por el
    # valor agregado recupera la tasa reportada ponderada (en puntos porcentuales).
    selected["rentabilidad_anual_ea_pct"] = (
        selected["rent_anual_por_valor"] / selected["valor_fondos"]
    )
    selected["rentabilidad_mensual_ea_pct"] = (
        selected["rent_mensual_por_valor"] / selected["valor_fondos"]
    )
    if not selected["rentabilidad_anual_ea_pct"].map(pd.notna).all():
        raise ValueError("La tasa anual derivada contiene valores faltantes")

    result = selected[
        [
            "fecha_corte",
            "rentabilidad_anual_ea_pct",
            "rentabilidad_mensual_ea_pct",
            "valor_fondos",
            "inversionistas",
            "registros",
        ]
    ].sort_values("fecha_corte")
    result = result.rename(
        columns={
            "fecha_corte": "fecha",
            "valor_fondos": "valor_fondos_cop",
            "inversionistas": "inversionistas_reportados_no_deduplicados",
            "registros": "registros_fic_subyacentes",
        }
    )
    result["fecha"] = result["fecha"].dt.strftime("%Y-%m-%d")
    return result


def write_outputs(series: pd.DataFrame, reference: dict, source_path: Path) -> dict:
    REPORTS.mkdir(parents=True, exist_ok=True)
    csv_path = REPORTS / "fic_market_money_annual_return.csv"
    png_path = REPORTS / "fic_market_money_annual_return.png"
    summary_path = REPORTS / "fic_market_money_summary.json"
    series.to_csv(csv_path, index=False, float_format="%.8f")

    rates = series["rentabilidad_anual_ea_pct"]
    latest = series.iloc[-1]
    summary = {
        "source_dataset_id": reference["dataset_id"],
        "source_sha256": sha256_file(source_path),
        "source_downloaded_utc": reference["downloaded_utc"],
        "series_selection": reference["selection"],
        "first_date": series.iloc[0]["fecha"],
        "latest_date": latest["fecha"],
        "observations": int(len(series)),
        "latest_underlying_fic_records": int(latest["registros_fic_subyacentes"]),
        "latest_fund_value_cop": float(latest["valor_fondos_cop"]),
        "latest_reported_investor_count_sum_not_unique": int(
            latest["inversionistas_reportados_no_deduplicados"]
        ),
        "latest_value_weighted_reported_annual_effective_return_pct": float(
            latest["rentabilidad_anual_ea_pct"]
        ),
        "annual_effective_return_pct_quantiles": {
            str(q): float(rates.quantile(q)) for q in [0.0, 0.1, 0.5, 0.9, 1.0]
        },
        "method": "sum(reported annual effective rate × fund value) / sum(fund value)",
        "interpretation": "Descriptive subtype-level weighted reported rate; not a portfolio time series or performance attribution.",
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")

    dates = pd.to_datetime(series["fecha"])
    smooth = rates.rolling(window=30, min_periods=15).median()
    fig, ax = plt.subplots(figsize=(12, 6.5), constrained_layout=True)
    ax.plot(dates, rates, color="#9aa6b2", linewidth=0.7, alpha=0.62, label="Tasa anual reportada ponderada")
    ax.plot(dates, smooth, color="#174a6e", linewidth=2.0, label="Mediana móvil de 30 cortes")
    ax.scatter(
        dates.iloc[-1], rates.iloc[-1], s=55, color="#c65f34", zorder=4,
        label=f"Último corte: {rates.iloc[-1]:.2f}% EA",
    )
    ax.set_title("FIC de mercado monetario: tasa efectiva anual reportada")
    ax.set_ylabel("Porcentaje efectivo anual, ponderado por valor del fondo")
    ax.set_xlabel("Fecha de corte SFC")
    ax.grid(axis="y", alpha=0.22)
    ax.legend(frameon=False, loc="best")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.text(
        0.01,
        0.005,
        "Serie agregada por subtipo y entidad; las ventanas de rentabilidad se superponen y no son retornos diarios independientes.",
        fontsize=8,
        color="#45515c",
    )
    fig.savefig(png_path, dpi=180, facecolor="white")
    plt.close(fig)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-csv", required=True, type=Path, help="Snapshot CSV externo exacto")
    args = parser.parse_args()

    reference = json.loads(REFERENCE_PATH.read_text())
    source_path = args.source_csv.expanduser().resolve()
    data = load_source(source_path, reference)
    series = build_series(data, reference)
    summary = write_outputs(series, reference, source_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
