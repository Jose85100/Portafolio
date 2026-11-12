#!/usr/bin/env python3
"""DANE observed inflation–activity association, with source hashes checked."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
REPORT_DIR = ROOT / "reports"
IPC_SHA = "4e8366bf2d03d4bdc15d14b1b21b12a6eec6c3695926abd503a430858ef74e2e"
IPC_BYTES = 40540
ISE_SHA = "4e333c97b6558eb7e1b82d17fb8a0aa966f9113c87f099fa000f2390a3d7a199"
ISE_BYTES = 487882
IPC_DANE_PAGE = "https://www.dane.gov.co/index.php/estadisticas-por-tema/precios-y-costos/indice-de-precios-al-consumidor-ipc/ipc-historico"
ISE_DANE_PAGE = "https://www.dane.gov.co/index.php/estadisticas-por-tema/cuentas-nacionales/indicador-de-seguimiento-a-la-economia-ise"


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_file(path: Path, expected_sha: str, expected_bytes: int, label: str) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"{label}: no existe la ruta --{label}-source: {path}")
    digest = hash_file(path)
    size = path.stat().st_size
    if digest != expected_sha or size != expected_bytes:
        raise ValueError(f"{label}: snapshot distinto; bytes={size}, sha256={digest}")
    return digest


def parse_cpi(path: Path) -> tuple[dict[str, float], dict]:
    digest = check_file(path, IPC_SHA, IPC_BYTES, "ipc")
    wb = load_workbook(path, read_only=True, data_only=True)
    if "IndicesIPC" not in wb.sheetnames:
        raise ValueError("Falta la hoja DANE `IndicesIPC`")
    ws = wb["IndicesIPC"]
    rows = list(ws.iter_rows(min_row=9, max_row=21, values_only=True))
    years = rows[0]
    values: dict[str, float] = {}
    for month_idx, row in enumerate(rows[1:], start=1):
        month = month_idx
        for col, year in enumerate(years[1:], start=1):
            value = row[col]
            if year is None or value is None:
                continue
            if not isinstance(year, int) or not isinstance(value, (int, float)) or value <= 0:
                raise ValueError(f"IPC no válido en hoja IndicesIPC, año={year}, mes={month}")
            values[f"{year}-{month:02d}"] = float(value)
    wb.close()
    if len(values) != 286 or min(values) != "2003-01" or max(values) != "2026-10":
        raise ValueError(f"Cobertura IPC inesperada: n={len(values)}, inicio={min(values)}, fin={max(values)}")
    inflation: dict[str, float] = {}
    for period, index in values.items():
        year, month = map(int, period.split("-"))
        prior = f"{year-1}-{month:02d}"
        if prior in values:
            inflation[period] = 100 * (index / values[prior] - 1)
    meta = {
        "source": "DANE, IPC, índice total nacional empalmado, base diciembre de 2018=100",
        "source_page": IPC_DANE_PAGE,
        "source_file": path.name,
        "source_bytes": path.stat().st_size,
        "source_sha256": digest,
        "sheet": "IndicesIPC",
        "source_grain": "Colombia × mes",
        "source_coverage": "2003-01 to 2026-10",
        "source_release": "DANE November 2026; source workbook says updated 2026-11-09",
        "transformation": "inflación anual (%) = 100 × (IPC_t / IPC_(t-12) − 1)",
    }
    return inflation, meta


def parse_ise(path: Path) -> tuple[dict[str, float], dict]:
    digest = check_file(path, ISE_SHA, ISE_BYTES, "ise")
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb["Cuadro 1"]
    data_row = None
    for row in ws.iter_rows(min_row=57, max_row=57, values_only=True):
        data_row = row
    if data_row is None or data_row[0] != "Indicador de Seguimiento a la Economía":
        raise ValueError("No se encontró el renglón total ISE esperado en Cuadro 1, fila 57")
    growth = {}
    for col in range(14, 261):
        year = 2006 + (col - 14) // 12
        month = (col - 14) % 12 + 1
        value = data_row[col - 1]
        if not isinstance(value, (int, float)) or not np.isfinite(value):
            raise ValueError(f"ISE no válido para {year}-{month:02d}")
        growth[f"{year}-{month:02d}"] = float(value)
    wb.close()
    if len(growth) != 247 or min(growth) != "2006-01" or max(growth) != "2026-07":
        raise ValueError(f"Cobertura ISE inesperada: n={len(growth)}, inicio={min(growth)}, fin={max(growth)}")
    meta = {
        "source": "DANE, ISE, serie original, fila total de tasas de crecimiento anuales",
        "source_page": ISE_DANE_PAGE,
        "drive_file_id": "1y85mYZ4aPD4IorJx53M8XR69JM1GrzRn",
        "atlas_manifest_vintage": "2026-10-08",
        "source_file": path.name,
        "source_bytes": path.stat().st_size,
        "source_sha256": digest,
        "sheet": "Cuadro 1; Indicador de Seguimiento a la Economía",
        "source_grain": "Colombia × mes",
        "source_coverage": "2006-01 to 2026-07; latest year preliminary",
        "transformation": "se usa directamente la variación anual reportada por DANE (%)",
    }
    return growth, meta


def fit_lags(sample: pd.DataFrame, include_trend: bool = True, drop_years: tuple[int, ...] = ()):
    x = pd.DataFrame(index=sample.index)
    for lag in range(4):
        x[f"ise_lag{lag}"] = sample["ise_growth_yoy_pct"].shift(lag)
    x = pd.concat([x, pd.get_dummies(sample.index.month, prefix="month", drop_first=True, dtype=float).set_axis(sample.index)], axis=1)
    if include_trend:
        x["linear_trend_per_decade"] = np.arange(len(sample)) / 120
    model = pd.concat([sample[["delta_inflation_pp"]], x], axis=1).dropna()
    if drop_years:
        model = model.loc[~model.index.year.isin(drop_years)]
    y = model.pop("delta_inflation_pp")
    design = sm.add_constant(model, has_constant="add").astype(float)
    return sm.OLS(y, design).fit(cov_type="HAC", cov_kwds={"maxlags": 6}), design.columns


def sum_effect(result, columns) -> dict:
    contrast = np.zeros(len(columns))
    for i, col in enumerate(columns):
        if col in {f"ise_lag{lag}" for lag in range(4)}:
            contrast[i] = 1
    estimate = float(contrast @ result.params.to_numpy())
    variance = float(contrast @ result.cov_params().to_numpy() @ contrast)
    se = float(np.sqrt(max(variance, 0)))
    return {"estimate": estimate, "hac_se": se, "ci95_low": estimate - 1.96 * se, "ci95_high": estimate + 1.96 * se}


def build(ipc_path: Path, ise_path: Path) -> None:
    ipc, ipc_meta = parse_cpi(ipc_path)
    ise, ise_meta = parse_ise(ise_path)
    common = sorted(set(ipc).intersection(ise))
    records = []
    for period in common:
        year, month = map(int, period.split("-"))
        prior = f"{year-1}-{month:02d}"
        previous = f"{year-1}-{month:02d}"
        # delta of annual inflation uses adjacent monthly year-over-year rates.
        prior_month = f"{year if month > 1 else year-1}-{month-1:02d}" if month > 1 else f"{year-1}-12"
        if prior_month not in ipc:
            continue
        records.append({
            "date": period,
            "inflation_yoy_pct": ipc[period],
            "delta_inflation_pp": ipc[period] - ipc[prior_month],
            "ise_growth_yoy_pct": ise[period],
            "period_status": "preliminar/provisional ISE" if year >= 2024 else "según vintage observado",
        })
    frame = pd.DataFrame(records)
    frame["date"] = pd.PeriodIndex(frame["date"], freq="M")
    frame = frame.set_index("date").sort_index()
    if len(frame) != 247 or str(frame.index[0]) != "2006-01" or str(frame.index[-1]) != "2026-07":
        raise ValueError(f"Muestra emparejada inesperada: n={len(frame)}, inicio={frame.index[0]}, fin={frame.index[-1]}")

    model, columns = fit_lags(frame, include_trend=True)
    sensitivity, sens_columns = fit_lags(frame, include_trend=False)
    no_event, event_columns = fit_lags(frame, include_trend=True, drop_years=(2020, 2021))
    cumulative = sum_effect(model, columns)
    cumulative_sens = sum_effect(sensitivity, sens_columns)
    cumulative_no_event = sum_effect(no_event, event_columns)
    corr = float(frame["delta_inflation_pp"].corr(frame["ise_growth_yoy_pct"]))
    result_df = pd.DataFrame({"date": frame.index.astype(str), **{c: frame[c].to_numpy() for c in frame.columns}})

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "figures").mkdir(parents=True, exist_ok=True)
    result_df.to_csv(REPORT_DIR / "paired_monthly_series.csv", index=False, float_format="%.8f")
    lag_rows = []
    for lag in range(4):
        key = f"ise_lag{lag}"
        param_index = list(columns).index(key)
        lag_rows.append({"lag_months": lag, "coefficient": float(model.params.iloc[param_index]), "hac_se": float(model.bse.iloc[param_index]),
                         "ci95_low": float(model.conf_int().iloc[param_index, 0]), "ci95_high": float(model.conf_int().iloc[param_index, 1])})
    with (REPORT_DIR / "distributed_lag_coefficients.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(lag_rows[0]))
        writer.writeheader(); writer.writerows(lag_rows)

    manifest = {
        "sources": [ipc_meta, ise_meta],
        "paired_sample": {"start": str(frame.index[0]), "end": str(frame.index[-1]), "months": len(frame)},
        "dependent_variable": "delta_inflation_pp = change from prior month in 12-month headline CPI inflation, percentage points",
        "activity_proxy": "DANE original ISE year-over-year growth, percent",
        "regression": "OLS: Δinflation_yoy_t on ISE_growth_yoy_t,...,ISE_growth_yoy_(t-3), month effects, linear trend; HAC maxlags=6",
        "regression_observations": int(model.nobs),
        "sensitivity_without_trend_observations": int(sensitivity.nobs),
        "sensitivity_excluding_2020_2021_outcomes_observations": int(no_event.nobs),
        "cumulative_four_month_association": cumulative,
        "sensitivity_without_trend": cumulative_sens,
        "sensitivity_excluding_outcomes_2020_2021": cumulative_no_event,
        "contemporaneous_correlation": corr,
        "interpretation": "descriptive inflation-activity association; not Phillips curve structural slope or causal effect",
        "raw_path_policy": "sources are passed at runtime; local paths are not persisted; canonical raw files are not copied into this product",
    }
    (DATA_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    dates = frame.index.to_timestamp()
    fig, axes = plt.subplots(2, 1, figsize=(10, 7.1), constrained_layout=True)
    axes[0].plot(dates, frame["inflation_yoy_pct"], color="#A34C3A", linewidth=1.5)
    axes[0].axhline(0, color="#444", linewidth=.7)
    axes[0].set_title("Inflación observada: variación anual del IPC total", loc="left", weight="bold")
    axes[0].set_ylabel("Porcentaje interanual")
    axes[0].grid(axis="y", alpha=.2)
    axes[1].plot(dates, frame["ise_growth_yoy_pct"], color="#17677B", linewidth=1.5)
    axes[1].axhline(0, color="#444", linewidth=.7)
    axes[1].set_title("Actividad observada: variación anual del ISE original", loc="left", weight="bold")
    axes[1].set_ylabel("Porcentaje interanual")
    axes[1].grid(axis="y", alpha=.2)
    fig.suptitle("Colombia · DANE · datos observados y vintage documentado", fontsize=14, weight="bold")
    fig.savefig(REPORT_DIR / "figures" / "inflation_activity_series.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    beta = [r["coefficient"] for r in lag_rows]
    low = [r["ci95_low"] for r in lag_rows]
    high = [r["ci95_high"] for r in lag_rows]
    x = np.arange(4)
    fig, ax = plt.subplots(figsize=(8.8, 4.8), constrained_layout=True)
    ax.errorbar(x, beta, yerr=[np.array(beta)-np.array(low), np.array(high)-np.array(beta)], fmt="o", color="#17677B", capsize=4)
    ax.axhline(0, color="#444", linewidth=.8)
    ax.set_xticks(x, labels=["t", "t−1", "t−2", "t−3"])
    ax.set_xlabel("Meses de rezago del crecimiento anual del ISE")
    ax.set_ylabel("Δ inflación anual (pp) por 1 pp de crecimiento ISE")
    ax.set_title("Asociación distribuida con IC HAC 95%", loc="left", weight="bold")
    ax.grid(axis="y", alpha=.2)
    fig.savefig(REPORT_DIR / "figures" / "distributed_lag_association.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    last = frame.iloc[-1]
    report = f"""# Aplicación observada: inflación realizada y actividad (proxy)

## Resultado

En {len(frame)} meses emparejados entre {frame.index[0]} y {frame.index[-1]}, la asociación contemporánea entre crecimiento anual del ISE y el cambio mensual en inflación interanual es `r = {corr:.3f}`. La regresión usa {int(model.nobs)} observaciones tras formar tres rezagos. Con efectos de mes, tendencia lineal y errores HAC(6), la suma de los cuatro coeficientes distribuidos es {cumulative['estimate']:.4f} pp de cambio de inflación anual por cada 1 pp del crecimiento anual del ISE (IC 95% [{cumulative['ci95_low']:.4f}, {cumulative['ci95_high']:.4f}]); no es una respuesta impulso estructural. Al retirar la tendencia, la suma es {cumulative_sens['estimate']:.4f} (IC 95% [{cumulative_sens['ci95_low']:.4f}, {cumulative_sens['ci95_high']:.4f}]); al excluir outcomes de 2020–2021 (n={int(no_event.nobs)}) es {cumulative_no_event['estimate']:.4f} (IC 95% [{cumulative_no_event['ci95_low']:.4f}, {cumulative_no_event['ci95_high']:.4f}]). En esta sensibilidad se conservan las observaciones de actividad rezagadas, pero se excluyen los meses 2020–2021 como outcomes.

La última observación emparejada es {frame.index[-1]}: inflación anual {last['inflation_yoy_pct']:.2f}% e ISE anual {last['ise_growth_yoy_pct']:.2f}%. El dato de actividad es preliminar.

![Series observadas](figures/inflation_activity_series.png)

![Coeficientes distribuidos](figures/distributed_lag_association.png)

## Variables y método

La inflación se calcula como `100 × (IPC_t / IPC_(t−12) − 1)` con el índice total empalmado de DANE; la variable dependiente es su cambio en puntos porcentuales frente al mes previo. La actividad es la variación anual del ISE original publicada por DANE. Se estiman cuatro rezagos mensuales en una regresión lineal con efectos fijos de mes, tendencia lineal y covarianza HAC con seis rezagos. Los intervalos no se interpretan como identificación causal.

La especificación es un diagnóstico de comovimiento de inflación realizada y actividad mensual. No es la ecuación de Phillips estructural: no observa expectativas de inflación ni una brecha del producto; el crecimiento del ISE es un proxy de actividad, no el output gap. Los rezagos contemporáneos son endógenos a choques de oferta, demanda y política monetaria.

## Fuentes, vintage y reproducción

- IPC: [DANE, histórico del IPC]({IPC_DANE_PAGE}); serie empalmada nacional, índice base diciembre de 2018=100, archivo actualizado 9-nov-2026, hash `{ipc_meta['source_sha256']}`.
- Actividad: [DANE, ISE]({ISE_DANE_PAGE}); serie original, Cuadro 1, enero de 2006–julio de 2026; el Atlas registra el archivo en su manifiesto 2026-10-08; hash `{ise_meta['source_sha256']}`.

Los dos XLSX fuente se reciben por ruta, se verifican por tamaño y SHA-256 y no se copian a este producto. El IPC se toma del snapshot DANE local ya disponible en el companion de pass-through; el ISE se toma del archivo DANE en `Master_DATOS/.../01_RAW`. Desde la raíz del portafolio:

```bash
python3 -m pip install openpyxl numpy pandas statsmodels matplotlib
python3 01-macroeconomics/03-inflation-expectations-phillips/observed_application.py \\
  --ipc-source 01-macroeconomics/05-exchange-rate-pass-through/data/raw/dane-ipc-empalme-2003-oct2026.xlsx \\
  --ise-source "/ruta/a/Master_DATOS/ATLAS_ECONOMICO_COLOMBIA/01_RAW/dane_ise_jul2026.xlsx"
```

Salidas derivadas: `reports/paired_monthly_series.csv`, `reports/distributed_lag_coefficients.csv`, `reports/figures/` y `data/manifest.json`. El manifiesto registra hashes, rutas de fuente sin ruta local, muestra, fórmula, modelo y límites.

## Uso y límites

El resultado puede orientar si merece la pena obtener expectativas, brecha de producto y una identificación de choques antes de estimar una Phillips estructural. No debe usarse para fijar precios, pronosticar inflación ni evaluar la regla monetaria. Las revisiones de ISE, la serie empalmada del IPC, la dependencia serial y la omisión de expectativas/costos sectoriales limitan cualquier lectura estructural.

El notebook sintético se mantiene intacto: sirve para analizar el sesgo de estimadores en procesos controlados. La edición observada solo describe una relación de datos y no valida el mecanismo.
"""
    (REPORT_DIR / "observed_application.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ipc-source", required=True, type=Path, help="Ruta al XLSX oficial de IPC empalmado")
    parser.add_argument("--ise-source", required=True, type=Path, help="Ruta al XLSX oficial ISE del Atlas")
    args = parser.parse_args()
    build(args.ipc_source.expanduser(), args.ise_source.expanduser())
    manifest = json.loads((DATA_DIR / "manifest.json").read_text(encoding="utf-8"))
    print(f"n={manifest['paired_sample']['months']}; period={manifest['paired_sample']['start']}..{manifest['paired_sample']['end']}")
    print(f"sum_beta={manifest['cumulative_four_month_association']['estimate']:.6f}; ci95=[{manifest['cumulative_four_month_association']['ci95_low']:.6f}, {manifest['cumulative_four_month_association']['ci95_high']:.6f}]")
