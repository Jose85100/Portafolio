"""Compare shuffled and time-ordered validation on observed Colombian CPI."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold, TimeSeriesSplit, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "dane-ipc-monthly.csv"
OUT = ROOT / "reports"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    cpi = pd.read_csv(SOURCE, parse_dates=["month"], index_col="month")["ipc_total_nacional"]
    monthly_inflation = cpi.pct_change().mul(100)
    frame = pd.DataFrame({f"lag_{lag}": monthly_inflation.shift(lag) for lag in range(1, 13)})
    frame["target"] = monthly_inflation
    frame = frame.dropna()
    # Last 24 months form a final chronological holdout. Both CV designs see
    # only the earlier training block; scaling is fit inside each fold.
    train, test = frame.iloc[:-24], frame.iloc[-24:]
    X_train, y_train = train.drop(columns="target"), train["target"]
    X_test, y_test = test.drop(columns="target"), test["target"]
    model = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    shuffled = KFold(n_splits=5, shuffle=True, random_state=2026)
    temporal = TimeSeriesSplit(n_splits=5, test_size=12, gap=0)
    shuffled_rmse = np.sqrt(-cross_val_score(model, X_train, y_train, cv=shuffled, scoring="neg_mean_squared_error"))
    temporal_rmse = np.sqrt(-cross_val_score(model, X_train, y_train, cv=temporal, scoring="neg_mean_squared_error"))
    model.fit(X_train, y_train)
    prediction = model.predict(X_test)
    persistence = X_test["lag_1"].to_numpy()
    final_rmse = float(np.sqrt(mean_squared_error(y_test, prediction)))
    persistence_rmse = float(np.sqrt(mean_squared_error(y_test, persistence)))
    final_mae = float(mean_absolute_error(y_test, prediction))
    results = {
        "source": "DANE IPC total nacional, índices de empalme, 2003-01 a 2026-10",
        "source_url": "https://www.dane.gov.co/files/operaciones/IPC/oct2026/anex-IPC-Indices-oct2026.xlsx",
        "publication_date": "2026-11-09",
        "source_xlsx_sha256": "4e8366bf2d03d4bdc15d14b1b21b12a6eec6c3695926abd503a430858ef74e2e",
        "input_csv_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "grain": "una observación mensual; target = inflación mensual porcentual del IPC total nacional",
        "features": "12 rezagos de inflación mensual; StandardScaler dentro del fold; Ridge(alpha=1)",
        "training_period": [train.index.min().strftime("%Y-%m"), train.index.max().strftime("%Y-%m")],
        "holdout_period": [test.index.min().strftime("%Y-%m"), test.index.max().strftime("%Y-%m")],
        "random_kfold_rmse_mean": float(shuffled_rmse.mean()),
        "random_kfold_rmse_sd": float(shuffled_rmse.std(ddof=1)),
        "time_series_split_rmse_mean": float(temporal_rmse.mean()),
        "time_series_split_rmse_sd": float(temporal_rmse.std(ddof=1)),
        "holdout_model_rmse": final_rmse,
        "holdout_model_mae": final_mae,
        "holdout_persistence_rmse": persistence_rmse,
        "controls": ["últimos 24 meses fuera de todas las folds de entrenamiento", "preprocesamiento ajustado dentro de cada fold", "mismos predictores y estimador en ambos CV", "comparación adicional contra persistencia lag-1"],
        "limitations": ["Serie macroeconómica agregada, un solo país y una sola ventana; no representa validación de riesgo crediticio ni cartera de clientes.", "El dato del holdout ya era publicado al congelar el snapshot; es evaluación retrospectiva, no pronóstico en tiempo real.", "El diseño compara esquemas de validación, no busca optimizar ni seleccionar un modelo para producción."]
    }
    pred = pd.DataFrame({"observed_monthly_inflation_pct": y_test, "ridge_forecast_pct": prediction,
                         "persistence_lag1_pct": persistence}, index=test.index)
    pred.to_csv(OUT / "official_holdout.csv", index_label="month")
    (OUT / "official_cv_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].boxplot([shuffled_rmse, temporal_rmse], tick_labels=["KFold aleatorio\n5 folds", "TimeSeriesSplit\n5 × 12 meses"], showmeans=True)
    axes[0].set_ylabel("RMSE por fold (pp)")
    axes[0].set_title("Validación dentro del bloque de entrenamiento")
    axes[0].grid(axis="y", alpha=.2)
    dates = test.index
    axes[1].plot(dates, y_test, marker="o", color="#111827", label="DANE observado")
    axes[1].plot(dates, prediction, color="#007a78", label="Ridge")
    axes[1].plot(dates, persistence, color="#d97706", ls="--", label="Persistencia lag-1")
    axes[1].set_title(f"Holdout cronológico · RMSE Ridge={final_rmse:.3f} pp")
    axes[1].set_ylabel("Inflación mensual (%)")
    axes[1].grid(alpha=.2)
    axes[1].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "official_cv_comparison.png", dpi=170)
    plt.close(fig)
    print(f"Snapshot CSV SHA-256: {results['input_csv_sha256']}")
    print(f"Train {results['training_period'][0]}–{results['training_period'][1]} | holdout {results['holdout_period'][0]}–{results['holdout_period'][1]}")
    print(f"KFold shuffled RMSE: {shuffled_rmse.mean():.4f} ± {shuffled_rmse.std(ddof=1):.4f} pp")
    print(f"TimeSeriesSplit RMSE: {temporal_rmse.mean():.4f} ± {temporal_rmse.std(ddof=1):.4f} pp")
    print(f"Holdout RMSE model/persistence: {final_rmse:.4f}/{persistence_rmse:.4f} pp")


if __name__ == "__main__":
    main()
