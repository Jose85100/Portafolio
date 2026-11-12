"""Evaluate the existing seasonal ARIMA workflow on DANE's official CPI index."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "dane-ipc-indices-oct2026.xlsx"
OUT = ROOT / "reports"


def read_monthly_cpi(path: Path) -> pd.Series:
    raw = pd.read_excel(path, sheet_name="IndicesIPC", header=None)
    header = next(i for i, row in raw.iterrows() if str(row.iloc[0]).strip() == "Mes")
    table = raw.iloc[header + 1 :].copy()
    table = table[table.iloc[:, 0].astype(str).str.strip().isin(
        ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    )]
    month_map = {name: i for i, name in enumerate(
        ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], 1
    )}
    records = []
    for _, row in table.iterrows():
        month = str(row.iloc[0]).strip()
        for col in range(1, len(row)):
            year = pd.to_numeric(raw.iloc[header, col], errors="coerce")
            value = pd.to_numeric(row.iloc[col], errors="coerce")
            if pd.notna(year) and pd.notna(value):
                records.append((pd.Period(year=int(year), month=month_map[month], freq="M"), float(value)))
    series = pd.Series(dict(records), dtype=float).sort_index()
    if series.index.has_duplicates or series.isna().any() or not series.index.is_monotonic_increasing:
        raise ValueError("La serie tiene duplicados, vacíos u orden inválido")
    expected = pd.period_range(series.index.min(), series.index.max(), freq="M")
    if not series.index.equals(expected):
        raise ValueError("La serie mensual tiene meses faltantes")
    return series


def rmse(actual, pred) -> float:
    return float(np.sqrt(np.mean((np.asarray(actual) - np.asarray(pred)) ** 2)))


def main() -> None:
    OUT.mkdir(exist_ok=True)
    index = read_monthly_cpi(SOURCE)
    index.rename("ipc_total_nacional").to_csv(OUT / "dane_ipc_monthly_extracted.csv", index_label="month")
    # The index is converted to 12-month inflation; the first 12 observations
    # are unavailable by construction and are dropped before the split.
    yoy = (index / index.shift(12) - 1).mul(100).dropna()
    horizon = 24
    train, test = yoy.iloc[:-horizon], yoy.iloc[-horizon:]
    best, best_aic, best_order = None, np.inf, None
    for p, d, q in itertools.product(range(3), range(2), range(3)):
        try:
            fit = SARIMAX(train, order=(p, d, q), seasonal_order=(1, 0, 0, 12),
                          enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
        except Exception:
            continue
        if np.isfinite(fit.aic) and fit.aic < best_aic:
            best, best_aic, best_order = fit, float(fit.aic), (p, d, q)
    if best is None:
        raise RuntimeError("No convergent model in the declared AIC grid")
    forecast = best.forecast(horizon)
    seasonal_naive = pd.Series(np.tile(train.iloc[-12:].to_numpy(), 2), index=test.index)
    metrics = {"model_rmse_pp": rmse(test, forecast), "seasonal_naive_rmse_pp": rmse(test, seasonal_naive),
               "model_mae_pp": float(np.mean(np.abs(test - forecast))),
               "seasonal_naive_mae_pp": float(np.mean(np.abs(test - seasonal_naive)))}
    pd.DataFrame({"actual_inflation_yoy_pct": test, "sarima_forecast_pct": forecast,
                  "seasonal_naive_pct": seasonal_naive}).to_csv(OUT / "official_forecast.csv", index_label="month")
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.plot(train.index.to_timestamp(), train, color="#6b7280", lw=1, label="Entrenamiento: inflación anual")
    ax.plot(test.index.to_timestamp(), test, color="#111827", lw=2, label="Observado DANE")
    ax.plot(test.index.to_timestamp(), forecast, color="#007a78", lw=2, label="SARIMA")
    ax.plot(test.index.to_timestamp(), seasonal_naive, color="#d97706", lw=1.5, ls="--", label="Ingenuo estacional")
    ax.axvline(test.index[0].to_timestamp(), color="#9ca3af", ls=":")
    ax.set(title="Inflación anual de Colombia: evaluación retrospectiva de 24 meses", ylabel="Porcentaje interanual", xlabel="Mes")
    ax.legend(frameon=False, ncol=2)
    ax.grid(alpha=.2)
    fig.tight_layout()
    fig.savefig(OUT / "official_forecast.png", dpi=170)
    plt.close(fig)
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    result = {"source": "DANE IPC, Índices. Serie de empalme 2003–2026 (octubre 2026)",
              "source_url": "https://www.dane.gov.co/files/operaciones/IPC/oct2026/anex-IPC-Indices-oct2026.xlsx",
              "publication_date": "2026-11-09",
              "snapshot_sha256": digest, "sheet": "IndicesIPC", "grain": "Total nacional, índice mensual, diciembre 2018=100",
              "observed_index_period": [str(index.index.min()), str(index.index.max())],
              "target": "Inflación anual derivada = 100 * (IPC_t / IPC_t-12 - 1)",
              "train_period": [str(train.index.min()), str(train.index.max())],
              "holdout_period": [str(test.index.min()), str(test.index.max())], "holdout_n": horizon,
              "selected_order": list(best_order), "seasonal_order": [1, 0, 0, 12], "aic": best_aic,
              "metrics": metrics,
              "controls": ["un mes por periodo, sin duplicados ni faltantes", "corte temporal anterior al holdout", "comparación con ingenuo estacional", "rejilla AIC fijada antes de observar el holdout"],
              "limitations": ["Evaluación retrospectiva de una sola ventana; no es backtest de orígenes rodantes.",
                              "La transformación anual solapa 11 meses entre observaciones.",
                              "Selección AIC en una rejilla pequeña; no se prueba intervención, cambio metodológico ni incertidumbre de parámetros.",
                              "No valida pronóstico en tiempo real, uso de política monetaria ni capacidad productiva."]}
    (OUT / "official_results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(f"DANE IPC SHA-256: {digest}")
    print(f"Holdout {result['holdout_period'][0]}–{result['holdout_period'][1]} | SARIMA{best_order}x(1,0,0,12) | AIC={best_aic:.2f}")
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}")


if __name__ == "__main__":
    main()
