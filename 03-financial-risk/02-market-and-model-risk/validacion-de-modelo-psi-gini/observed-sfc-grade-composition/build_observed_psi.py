#!/usr/bin/env python3
"""Compute descriptive PSI on SFC aggregate credit-grade balance mix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
REFERENCE_PATH = HERE / "data" / "source_reference.json"
DEFAULT_INPUT = REPO_ROOT / "03-financial-risk/01-credit-risk/credit-risk-products/perdida-esperada-pd-lgd-ead/observed-sfc-product-risk-mix/data/processed/sfc_product_risk_grade_mix_monthly.csv"
OUTPUT = HERE / "results"
FIGURES = HERE / "figures"
GRADE_COLUMNS = ["saldo_A", "saldo_B", "saldo_C", "saldo_D", "saldo_E"]
GRADE_LABELS = ["A", "B", "C", "D", "E"]
REQUIRED = {
    "fecha_corte",
    "unicap",
    "descrip_uc",
    "saldo_bruto",
    *GRADE_COLUMNS,
    "entidades_reportantes",
    "filas_entidad",
    "saldo_calificado_A_E",
    "saldo_D_E",
    "participacion_D_E_en_calificado_pct",
    "cobertura_calificacion_sobre_bruto_pct",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_and_validate(path: Path, reference: dict) -> pd.DataFrame:
    actual_hash = sha256_file(path)
    expected_hash = reference["reused_derived_input_sha256"]
    if actual_hash != expected_hash:
        raise ValueError(f"SHA-256 del derivado no coincide: {actual_hash} != {expected_hash}")
    data = pd.read_csv(path)
    missing = REQUIRED - set(data.columns)
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {sorted(missing)}")
    if len(data) != reference["reused_derived_input_rows"]:
        raise ValueError(f"Número de filas inesperado: {len(data)}")

    data["fecha_corte"] = pd.to_datetime(data["fecha_corte"], errors="coerce")
    if data["fecha_corte"].isna().any():
        raise ValueError("Hay fechas inválidas")
    if data.duplicated(["fecha_corte", "unicap"]).any():
        raise ValueError("La llave corte × producto no es única")

    numeric = ["unicap", "saldo_bruto", *GRADE_COLUMNS, "cobertura_calificacion_sobre_bruto_pct"]
    for column in numeric:
        data[column] = pd.to_numeric(data[column], errors="coerce")
        if data[column].isna().any() or not np.isfinite(data[column].to_numpy(dtype=float)).all():
            raise ValueError(f"La columna {column} tiene valores no numéricos o no finitos")
    return data


def period_distribution(product: pd.DataFrame, label: str, start: str, end: str) -> tuple[pd.Series, pd.Series, dict]:
    subset = product.loc[
        product["fecha_corte"].between(pd.Timestamp(start), pd.Timestamp(end))
    ].copy()
    if len(subset) != 24:
        raise ValueError(f"{label}: se esperaban 24 cortes mensuales y hay {len(subset)}")
    if subset["fecha_corte"].nunique() != 24:
        raise ValueError(f"{label}: hay fechas mensuales duplicadas o faltantes")
    if (subset[GRADE_COLUMNS] < 0).any().any():
        raise ValueError(f"{label}: saldos A-E negativos")
    if (subset["cobertura_calificacion_sobre_bruto_pct"] < 95.0).any():
        raise ValueError(f"{label}: la cobertura A-E cae debajo del umbral de 95%")
    total = subset[GRADE_COLUMNS].sum(axis=1)
    if (total <= 0).any():
        raise ValueError(f"{label}: saldo calificado no positivo")
    month_shares = subset[GRADE_COLUMNS].div(total, axis=0)
    mean_monthly = month_shares.mean(axis=0)
    pooled = subset[GRADE_COLUMNS].sum(axis=0) / subset[GRADE_COLUMNS].to_numpy().sum()
    diagnostics = {
        "start": str(subset["fecha_corte"].min().date()),
        "end": str(subset["fecha_corte"].max().date()),
        "months": int(len(subset)),
        "minimum_rated_balance_coverage_pct": float(subset["cobertura_calificacion_sobre_bruto_pct"].min()),
        "mean_rated_balance_coverage_pct": float(subset["cobertura_calificacion_sobre_bruto_pct"].mean()),
        "mean_monthly_product_balance": float(subset["saldo_bruto"].mean()),
    }
    return mean_monthly, pooled, diagnostics


def psi(expected: pd.Series, actual: pd.Series) -> float:
    # Small positive floor is a standard numerical guard for empty categories.
    # Renormalize after flooring so both vectors remain distributions.
    e = np.maximum(expected.to_numpy(dtype=float), 1e-6)
    a = np.maximum(actual.to_numpy(dtype=float), 1e-6)
    e /= e.sum()
    a /= a.sum()
    return float(np.sum((a - e) * np.log(a / e)))


def write_outputs(
    base_mean: pd.Series,
    recent_mean: pd.Series,
    base_pooled: pd.Series,
    recent_pooled: pd.Series,
    period_info: dict,
    reference: dict,
    input_path: Path,
) -> dict:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    base_mean.index = GRADE_LABELS
    recent_mean.index = GRADE_LABELS
    base_pooled.index = GRADE_LABELS
    recent_pooled.index = GRADE_LABELS

    mix_rows = []
    for grade in GRADE_LABELS:
        mix_rows.append(
            {
                "risk_grade": grade,
                "baseline_mean_monthly_share_pct": float(base_mean[grade] * 100),
                "recent_mean_monthly_share_pct": float(recent_mean[grade] * 100),
                "change_percentage_points": float((recent_mean[grade] - base_mean[grade]) * 100),
                "baseline_pooled_balance_share_pct": float(base_pooled[grade] * 100),
                "recent_pooled_balance_share_pct": float(recent_pooled[grade] * 100),
            }
        )
    mix = pd.DataFrame(mix_rows)
    psi_month_equal = psi(base_mean, recent_mean)
    psi_pooled_sensitivity = psi(base_pooled, recent_pooled)
    mix.to_csv(OUTPUT / "observed_risk_grade_mix.csv", index=False, float_format="%.8f")

    source_hash = reference["source_raw_sha256"]
    input_hash = sha256_file(input_path)
    summary = {
        "source_dataset_id": reference["dataset_id"],
        "source_raw_sha256": source_hash,
        "reused_derived_input_sha256": input_hash,
        "selected_product_code": reference["selection"]["product_code"],
        "selected_product_name": reference["selection"]["product_name"],
        "baseline_period": period_info["baseline"],
        "comparison_period": period_info["recent"],
        "category_order": GRADE_LABELS,
        "psi_mean_monthly_shares_equal_weighted_months": psi_month_equal,
        "psi_pooled_balances_sensitivity": psi_pooled_sensitivity,
        "psi_thresholds_note": "0.10/0.25 are common rules of thumb in score PSI discussions; not calibrated or valid operational thresholds for this aggregate balance-mix statistic.",
        "baseline_grade_shares_pct": {r["risk_grade"]: r["baseline_mean_monthly_share_pct"] for r in mix_rows},
        "recent_grade_shares_pct": {r["risk_grade"]: r["recent_mean_monthly_share_pct"] for r in mix_rows},
        "changes_percentage_points": {r["risk_grade"]: r["change_percentage_points"] for r in mix_rows},
        "interpretation": "Descriptive distribution shift in reported SFC product balances across rating grades; not score drift, model performance, default incidence or calibration.",
        "period_diagnostics": period_info,
        "months_excluded": 0,
    }
    (OUTPUT / "observed_psi_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")

    x = np.arange(len(GRADE_LABELS))
    width = 0.34
    fig, (ax_mix, ax_change) = plt.subplots(1, 2, figsize=(12, 5.5), gridspec_kw={"width_ratios": [1.4, 1]})
    ax_mix.bar(x - width / 2, base_mean.to_numpy() * 100, width, label="Base · 2018–2019", color="#537895")
    ax_mix.bar(x + width / 2, recent_mean.to_numpy() * 100, width, label="Comparación · 2024-09 a 2026-08", color="#e28b48")
    ax_mix.set_xticks(x, GRADE_LABELS)
    ax_mix.set_ylabel("Participación promedio mensual del saldo A–E (%)")
    ax_mix.set_xlabel("Calificación reportada por la SFC")
    ax_mix.set_title("Mezcla de saldo por calificación")
    ax_mix.grid(axis="y", alpha=0.22)
    ax_mix.legend(frameon=False, fontsize=8)
    for i, grade in enumerate(GRADE_LABELS):
        ax_mix.annotate(f"{base_mean[grade]*100:.2f}%", (i-width/2, base_mean[grade]*100), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=7)
        ax_mix.annotate(f"{recent_mean[grade]*100:.2f}%", (i+width/2, recent_mean[grade]*100), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=7)

    changes = (recent_mean - base_mean).to_numpy() * 100
    colors = ["#c65f34" if value < 0 else "#3a8c78" for value in changes]
    ax_change.barh(GRADE_LABELS, changes, color=colors)
    ax_change.axvline(0, color="#33414d", linewidth=0.8)
    ax_change.set_xlabel("Cambio de participación (puntos porcentuales)")
    ax_change.set_title(f"Cambio y PSI = {psi_month_equal:.4f}")
    ax_change.grid(axis="x", alpha=0.22)
    for i, value in enumerate(changes):
        ax_change.text(value / 2, i, f"{value:+.3f}", va="center", ha="center", fontsize=8, color="white", fontweight="bold")
    fig.suptitle("Crédito rotativo · mezcla de saldo SFC (agregado)", fontsize=14)
    fig.text(0.01, 0.01, "PSI sobre participaciones A–E; mezcla de balances agregados, no distribución de scores ni observaciones individuales.", fontsize=8, color="#45515c")
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(FIGURES / "observed_risk_grade_mix_psi.png", dpi=180, facecolor="white")
    plt.close(fig)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="CSV derivado oficial SFC ya disponible")
    args = parser.parse_args()
    input_path = args.input.expanduser().resolve()
    reference = json.loads(REFERENCE_PATH.read_text())
    data = read_and_validate(input_path, reference)
    choice = reference["selection"]
    product = data.loc[data["unicap"].eq(choice["product_code"])].copy()
    if product.empty or product["descrip_uc"].nunique() != 1 or product["descrip_uc"].iloc[0] != choice["product_name"]:
        raise ValueError("El código y nombre del producto no coinciden con la referencia")

    baseline = choice["baseline_period"]
    recent = choice["comparison_period"]
    base_mean, base_pooled, base_info = period_distribution(product, "baseline", *baseline)
    recent_mean, recent_pooled, recent_info = period_distribution(product, "recent", *recent)
    period_info = {"baseline": base_info, "recent": recent_info}
    summary = write_outputs(base_mean, recent_mean, base_pooled, recent_pooled, period_info, reference, input_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
