#!/usr/bin/env python3
"""Aggregate official SFC category-level IRL data for descriptive liquidity context."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import math
import argparse
import io
import subprocess
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data/sfc_irl_monthly_by_entity_type.csv"
MANIFEST = ROOT / "data/source_manifest.json"
OUT = ROOT / "results"
EXPECTED_SHA256 = "6ea7719b51d23faa4a5c5bfff2ab1893e082f10597645121f0dc0365f6b2d275"
EXPECTED_TYPES = {"Bancos", "Compañías de Financiamiento", "Cooperativas Financieras"}


def extract_category_snapshot(workbook_bytes: bytes) -> bytes:
    """Extract only SFC's already aggregated Por Tipo sheet; never retain Por Entidad."""
    source = pd.read_excel(io.BytesIO(workbook_bytes), sheet_name="Por Tipo", header=4, engine="openpyxl")
    source = source.dropna(subset=["Fecha"]).rename(columns={
        "Fecha": "date",
        "Tipo Entidad": "entity_type",
        "ALM PromedioMes": "alm_avg_month_thousand_cop",
        "RLN PromedioMes": "rln_avg_month_thousand_cop",
        "IRL": "irl_reported",
    })
    columns = ["date", "entity_type", "alm_avg_month_thousand_cop", "rln_avg_month_thousand_cop", "irl_reported"]
    source = source[columns].copy()
    source["date"] = pd.to_datetime(source["date"]).dt.strftime("%Y-%m-%d")
    buffer = io.StringIO()
    source.to_csv(buffer, index=False, float_format="%.6f")
    return buffer.getvalue().encode("utf-8")


def verify_official_workbook(manifest: dict) -> str:
    """Fetch source in memory and verify both original and category-only hashes."""
    # curl uses the system trust store on macOS in this environment; no TLS bypass is used.
    response = subprocess.run(
        ["curl", "--fail", "--location", "--silent", "--show-error", "--max-time", "60", manifest["source_file_url"]],
        check=True, capture_output=True,
    )
    workbook_bytes = response.stdout
    source_sha = hashlib.sha256(workbook_bytes).hexdigest()
    if source_sha != manifest["source_file_sha256"]:
        raise ValueError(f"El XLSX oficial cambió de contenido: {source_sha}; revise y gobierne la nueva versión")
    extracted = extract_category_snapshot(workbook_bytes)
    extracted_sha = hashlib.sha256(extracted).hexdigest()
    if extracted_sha != manifest["extracted_file_sha256"]:
        raise ValueError(f"La extracción category-level no coincide con el snapshot: {extracted_sha}")
    return source_sha


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-source", action="store_true", help="Descarga el XLSX oficial en memoria, reconstruye solo Por Tipo y verifica hashes; no guarda filas por entidad")
    args = parser.parse_args()
    raw = INPUT.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError(f"Hash inesperado para el snapshot IRL agregado: {digest}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("extracted_file_sha256") != digest:
        raise ValueError("Hash de entrada no coincide con el manifiesto")
    verified_source_sha = verify_official_workbook(manifest) if args.verify_source else None
    df = pd.read_csv(INPUT, parse_dates=["date"])
    required = {"date", "entity_type", "alm_avg_month_thousand_cop", "rln_avg_month_thousand_cop", "irl_reported"}
    if set(df.columns) != required:
        raise ValueError(f"Esquema inesperado: {df.columns.tolist()}")
    if df[["date", "entity_type"]].duplicated().any():
        raise ValueError("Hay fecha/tipo de entidad duplicados")
    if set(df.entity_type.unique()) != EXPECTED_TYPES:
        raise ValueError("Cambió la lista de tipos de entidad del snapshot")
    if not df[["alm_avg_month_thousand_cop", "rln_avg_month_thousand_cop", "irl_reported"]].apply(lambda col: col.map(math.isfinite)).all().all():
        raise ValueError("Hay importes o indicadores no finitos")
    if (df[["alm_avg_month_thousand_cop", "rln_avg_month_thousand_cop"]] < 0).any().any():
        raise ValueError("ALM/RLN no pueden ser negativos en este corte")
    counts = df.groupby("date").entity_type.nunique()
    if not (counts == len(EXPECTED_TYPES)).all() or len(counts) != 34:
        raise ValueError("Faltan tipos o periodos respecto del snapshot documentado")
    observed_months = pd.PeriodIndex(sorted(counts.index), freq="M")
    expected_months = pd.period_range("2020-03", "2022-12", freq="M")
    if not observed_months.equals(expected_months):
        raise ValueError("Calendario mensual discontinuo")
    # SFC expresses ALM/RLN in thousands of COP; sum type-level amounts and then form the ratio.
    monthly = df.groupby("date", as_index=False).agg(
        alm_avg_month_thousand_cop=("alm_avg_month_thousand_cop", "sum"),
        rln_avg_month_thousand_cop=("rln_avg_month_thousand_cop", "sum"),
        source_type_count=("entity_type", "nunique"),
    )
    monthly["irl_sector_ratio"] = monthly.alm_avg_month_thousand_cop / monthly.rln_avg_month_thousand_cop
    monthly["alm_avg_month_cop_billions"] = monthly.alm_avg_month_thousand_cop / 1_000_000
    monthly["rln_avg_month_cop_billions"] = monthly.rln_avg_month_thousand_cop / 1_000_000
    monthly["irl_monthly_change_pp"] = monthly.irl_sector_ratio.diff() * 100
    # Reported category ratios should agree with source amounts, allowing rounding to 3 decimals.
    type_calc = df.alm_avg_month_thousand_cop / df.rln_avg_month_thousand_cop
    rounding_gap = (type_calc - df.irl_reported).abs().max()
    if rounding_gap > 0.001:
        raise ValueError(f"Source IRL does not reconcile to ALM/RLN within rounding tolerance: {rounding_gap}")
    OUT.mkdir(parents=True, exist_ok=True)
    monthly.to_csv(OUT / "sfc_irl_sector_monthly.csv", index=False, date_format="%Y-%m-%d", float_format="%.6f")
    latest = monthly.iloc[-1]
    summary = {
        "purpose": "Descriptive, source-backed aggregate liquidity context; not corporate ALM validation or EVE/NII estimation",
        "source": "Superintendencia Financiera de Colombia (SFC), Indicador de Riesgo de Liquidez (IRL), sheet Por Tipo",
        "source_page": manifest["source_page"],
        "source_file_url": manifest["source_file_url"],
        "source_file_sha256": manifest["source_file_sha256"],
        "source_redownload_and_extraction_verified_this_run": bool(args.verify_source),
        "source_file_sha256_verified_this_run": verified_source_sha,
        "category_snapshot_sha256": digest,
        "source_downloaded_local_date": manifest["downloaded_local_date"],
        "snapshot_period": {"start": monthly.date.min().strftime("%Y-%m-%d"), "end": monthly.date.max().strftime("%Y-%m-%d"), "months": len(monthly)},
        "input_rows": len(df),
        "input_category_rows_retained": "Only aggregate entity-type totals (Bancos, Compañías de Financiamiento, Cooperativas Financieras); no individual-institution rows retained.",
        "source_reporting": "Monthly-average liquid market assets (ALM) and net liquidity requirement (RLN), in thousands of COP; IRL as reported by SFC.",
        "aggregation_method": "Sector IRL = sum(ALM by entity type) / sum(RLN by entity type), computed from category-level totals. This is not the arithmetic mean of category ratios.",
        "unit_conversion": "COP billions = source COP-thousands / 1,000,000",
        "type_ratio_reconciliation_max_abs_gap": float(rounding_gap),
        "latest_aggregate_observation": {"date": latest.date.strftime("%Y-%m-%d"), "alm_avg_month_cop_billions": float(latest.alm_avg_month_cop_billions), "rln_avg_month_cop_billions": float(latest.rln_avg_month_cop_billions), "irl_sector_ratio": float(latest.irl_sector_ratio), "irl_monthly_change_percentage_points": None if pd.isna(latest.irl_monthly_change_pp) else float(latest.irl_monthly_change_pp)},
        "limits": ["Source vintage ends 2022-12; it is not a current 2026 condition indicator.", "The IRL is a regulatory short-horizon liquidity measure, not interest-rate repricing, duration gap, EVE or NII.", "Category-level totals are already aggregated by SFC; no institution-level cash flows, behavioral assumptions, instrument repricing dates, hedges or outcomes are available here.", "Sector aggregation can mask institution heterogeneity and does not define a corporate or banking risk appetite threshold.", "No independent model validation or forecast/backtest is performed; this is a transparent descriptive calculation."]
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 7), sharex=True, constrained_layout=True)
    axes[0].plot(monthly.date, monthly.alm_avg_month_cop_billions, label="ALM promedio mensual", color="#245B7A", lw=1.8)
    axes[0].plot(monthly.date, monthly.rln_avg_month_cop_billions, label="RLN promedio mensual", color="#C16B43", lw=1.8)
    axes[0].set_ylabel("COP miles de millones")
    axes[0].set_title("Liquidez reportada por tipo: agregados SFC")
    axes[0].legend(frameon=False, ncol=2)
    axes[1].plot(monthly.date, monthly.irl_sector_ratio, color="#347A63", lw=1.8)
    axes[1].scatter(monthly.date.iloc[-1], latest.irl_sector_ratio, color="#7A5195", zorder=4)
    axes[1].annotate(f"{latest.irl_sector_ratio:.2f}×", (monthly.date.iloc[-1], latest.irl_sector_ratio), xytext=(-6, 9), textcoords="offset points", ha="right")
    axes[1].set_ylabel("ALM / RLN (veces)")
    axes[1].set_title("IRL sectorial derivado como razón de sumas")
    axes[1].set_xlabel("Fecha de corte")
    fig.suptitle("SFC | Contexto histórico agregado de riesgo de liquidez", fontsize=14, weight="bold")
    fig.text(.01, -.01, "Último corte del archivo histórico: dic-2022. La agregación no sustituye ALM por entidad ni sensibilidades EVE/NII.", fontsize=8)
    fig.savefig(OUT / "sfc_irl_aggregate_context.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(json.dumps({"period": summary["snapshot_period"], "latest": summary["latest_aggregate_observation"], "sha256": digest}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
