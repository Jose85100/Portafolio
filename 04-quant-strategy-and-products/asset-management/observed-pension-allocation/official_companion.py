#!/usr/bin/env python3
"""Observed SFC pension fund allocation snapshot, aggregated by investment class."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
REFERENCE = json.loads((ROOT / "data" / "source_reference.json").read_text(encoding="utf-8"))
REPORTS = ROOT / "reports"
PROFILE_ORDER = ["Conservador", "Moderado", "Mayor riesgo", "Retiro programado"]
PROFILE_PATTERNS = {
    "Conservador": "CONSERVADOR",
    "Moderado": "MODERADO",
    "Mayor riesgo": "MAYOR RIESGO",
    "Retiro programado": "RETIRO PROGRAMADO",
}
EXPECTED_PORTFOLIOS_PER_PROFILE = {
    "Conservador": 4,
    "Moderado": 3,
    "Mayor riesgo": 4,
    "Retiro programado": 4,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-csv", type=Path, required=True,
        help="Ruta externa de staging al snapshot agregado; el raw no se copia a este proyecto.",
    )
    return parser.parse_args()


def classify_profile(portfolio_name: str) -> str | None:
    upper = portfolio_name.upper()
    if not upper.startswith("FONDO DE PENSIONES"):
        return None
    for profile in PROFILE_ORDER:
        if PROFILE_PATTERNS[profile] in upper:
            return profile
    return None


def short_class_label(class_name: str) -> str:
    exact = {
        "Participaciones en fondos representativos de índices accionarios": "Fondos de índices accionarios",
        "Títulos de Tesorería - TES Pesos TF": "TES pesos TF",
        "Títulos de Tesorería - TES UVR": "TES UVR",
        "Participaciones en fondos de capital privado constituidos en el exterior": "Capital privado exterior",
        "Acciones con alta liquidez bursátil emitidas por entidades no vigiladas por la Superintendencia Financiera": "Acciones líquidas no vigiladas SFC",
        "Acciones con alta liquidez bursátil emitidas por entidades vigiladas por la Superintendencia Financiera": "Acciones líquidas vigiladas SFC",
        "Participaciciones en fondos mutuos o de inversión internacionales cuyo objetivo principal sea invertir en acciones": "Fondos internacionales de acciones",
        "Productos estructurados emitidos por bancos del exterior": "Estructurados de bancos extranjeros",
    }
    return exact.get(class_name, class_name)


def main() -> None:
    args = parse_args()
    if not args.source_csv.is_file():
        raise FileNotFoundError(f"No existe el snapshot de staging: {args.source_csv}")
    raw = args.source_csv.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != REFERENCE["sha256"]:
        raise ValueError(f"SHA-256 inesperado: {digest}; esperado {REFERENCE['sha256']}")

    required = ["fecha_de_corte", "nombre_patrimonio", "descripcion_clase_inversion", "valor_mercado", "dias_venc_por_valor", "titulos"]
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(text.splitlines())
    if reader.fieldnames != required:
        raise ValueError(f"Esquema inesperado: {reader.fieldnames}")
    rows: list[dict] = []
    keys = set()
    cut_dates = set()
    portfolio_names = set()
    classes = set()
    zero_market_values = 0
    for line_number, source_row in enumerate(reader, start=2):
        if any(not (source_row.get(k) or "").strip() for k in required):
            raise ValueError(f"Campo obligatorio vacío en fila {line_number}")
        cut_date = date.fromisoformat(source_row["fecha_de_corte"][:10])
        portfolio = source_row["nombre_patrimonio"].strip()
        asset_class = source_row["descripcion_clase_inversion"].strip()
        try:
            market_value = Decimal(source_row["valor_mercado"])
            title_count = int(Decimal(source_row["titulos"]))
            _weighted_days = Decimal(source_row["dias_venc_por_valor"])
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"Medida no numérica en fila {line_number}") from exc
        if not market_value.is_finite() or not _weighted_days.is_finite() or title_count < 0:
            raise ValueError(f"Medida fuera de dominio en fila {line_number}")
        key = (cut_date, portfolio, asset_class)
        if key in keys:
            raise ValueError(f"Duplicado en grano fecha×patrimonio×clase: {key}")
        keys.add(key)
        cut_dates.add(cut_date)
        portfolio_names.add(portfolio)
        classes.add(asset_class)
        zero_market_values += market_value == 0
        rows.append({"date": cut_date, "portfolio": portfolio, "asset_class": asset_class, "market_value": market_value})

    if len(rows) != REFERENCE["rows"] or len(cut_dates) != REFERENCE["distinct_cut_dates"]:
        raise ValueError(f"Volumen inesperado: filas={len(rows)}, cortes={len(cut_dates)}")
    if max(cut_dates).isoformat() != REFERENCE["latest_observation"]:
        raise ValueError(f"Corte máximo inesperado: {max(cut_dates)}")
    selected_date = date.fromisoformat(REFERENCE["latest_observation"])
    selected = [r for r in rows if r["date"] == selected_date and classify_profile(r["portfolio"]) is not None]
    if not selected:
        raise ValueError("No hay observaciones FPO para la fecha común esperada")
    if any(r["market_value"] < 0 for r in selected):
        raise ValueError("La fecha y población seleccionadas contienen valores de mercado negativos")

    portfolio_profiles: dict[str, str] = {}
    profile_class_totals: dict[str, defaultdict[str, Decimal]] = {p: defaultdict(Decimal) for p in PROFILE_ORDER}
    fund_class_totals: dict[tuple[str, str], defaultdict[str, Decimal]] = defaultdict(lambda: defaultdict(Decimal))
    profile_totals: dict[str, Decimal] = {p: Decimal(0) for p in PROFILE_ORDER}
    funds_by_profile: dict[str, set[str]] = {p: set() for p in PROFILE_ORDER}
    selected_classes: dict[str, set[str]] = {p: set() for p in PROFILE_ORDER}
    for row in selected:
        profile = classify_profile(row["portfolio"])
        portfolio_profiles[row["portfolio"]] = profile
        funds_by_profile[profile].add(row["portfolio"])
        profile_class_totals[profile][row["asset_class"]] += row["market_value"]
        fund_class_totals[(profile, row["portfolio"])][row["asset_class"]] += row["market_value"]
        profile_totals[profile] += row["market_value"]
        selected_classes[profile].add(row["asset_class"])

    for profile in PROFILE_ORDER:
        expected = EXPECTED_PORTFOLIOS_PER_PROFILE[profile]
        if len(funds_by_profile[profile]) != expected or profile_totals[profile] <= 0:
            raise ValueError(f"Cobertura inesperada para {profile}: {len(funds_by_profile[profile])} patrimonios")

    all_classes = sorted({c for profile in PROFILE_ORDER for c in profile_class_totals[profile]})
    pooled_shares: dict[str, dict[str, float]] = {}
    medians: dict[str, dict[str, float]] = {}
    concentration = {}
    for profile in PROFILE_ORDER:
        pooled_shares[profile] = {
            c: float(100 * profile_class_totals[profile][c] / profile_totals[profile])
            for c in all_classes
        }
        fund_shares = []
        for fund in sorted(funds_by_profile[profile]):
            fund_total = sum(fund_class_totals[(profile, fund)].values())
            fund_shares.append({c: float(100 * fund_class_totals[(profile, fund)][c] / fund_total) for c in all_classes})
        medians[profile] = {
            c: statistics.median([fund[c] for fund in fund_shares]) for c in all_classes
        }
        hhi = sum((pooled_shares[profile][c] / 100) ** 2 for c in all_classes) * 10_000
        concentration[profile] = {"hhi_by_reported_class": hhi, "effective_reported_classes": 10_000 / hhi}
        if abs(sum(pooled_shares[profile].values()) - 100) > 1e-8:
            raise ValueError(f"Los pesos de {profile} no suman 100%")

    grand_by_class = {c: sum(profile_class_totals[p][c] for p in PROFILE_ORDER) for c in all_classes}
    top_classes = sorted(all_classes, key=lambda c: grand_by_class[c], reverse=True)[:8]
    other_label = "Otras clases"
    heat_rows = top_classes + [other_label]
    heat = np.zeros((len(heat_rows), len(PROFILE_ORDER)), dtype=float)
    pooled_matrix = []
    for j, profile in enumerate(PROFILE_ORDER):
        for i, class_name in enumerate(top_classes):
            heat[i, j] = pooled_shares[profile][class_name]
            pooled_matrix.append((profile, class_name, profile_class_totals[profile][class_name], heat[i, j], medians[profile][class_name]))
        heat[-1, j] = 100 - heat[:-1, j].sum()
        pooled_matrix.append((profile, other_label, profile_totals[profile] * Decimal(str(heat[-1, j])) / Decimal(100), heat[-1, j], statistics.median([100 - sum(f[c] for c in top_classes) for f in [
            {c: float(100 * fund_class_totals[(profile, fund)][c] / sum(fund_class_totals[(profile, fund)].values())) for c in all_classes}
            for fund in sorted(funds_by_profile[profile])
        ]])))

    REPORTS.mkdir(exist_ok=True)
    with (REPORTS / "observed_allocation_by_profile.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["cut_date", "portfolio_profile", "investment_class_sfc", "market_value_cop_pooled", "pooled_weight_pct", "equal_portfolio_median_weight_pct", "n_source_portfolios"])
        for profile in PROFILE_ORDER:
            for class_name in all_classes:
                value = profile_class_totals[profile][class_name]
                writer.writerow([selected_date.isoformat(), profile, class_name, str(value), f"{pooled_shares[profile][class_name]:.8f}", f"{medians[profile][class_name]:.8f}", len(funds_by_profile[profile])])
            other_value = profile_totals[profile] * (Decimal(100) - sum(Decimal(str(pooled_shares[profile][c])) for c in top_classes)) / Decimal(100)
            other_median = statistics.median([
                100 - sum(float(100 * fund_class_totals[(profile, fund)][c] / sum(fund_class_totals[(profile, fund)].values())) for c in top_classes)
                for fund in sorted(funds_by_profile[profile])
            ])
            writer.writerow([selected_date.isoformat(), profile, other_label, str(other_value), f"{heat[-1, PROFILE_ORDER.index(profile)]:.8f}", f"{other_median:.8f}", len(funds_by_profile[profile])])

    profile_summary = {}
    for profile in PROFILE_ORDER:
        profile_summary[profile] = {
            "n_reported_portfolios": len(funds_by_profile[profile]),
            "n_investment_classes": len(profile_class_totals[profile]),
            "total_market_value_cop": str(profile_totals[profile]),
            "top_3_pooled_classes": [
                {"investment_class_sfc": c, "weight_pct": pooled_shares[profile][c]}
                for c in sorted(profile_class_totals[profile], key=profile_class_totals[profile].get, reverse=True)[:3]
            ],
            **concentration[profile],
        }
    summary = {
        "source": REFERENCE["source_name"],
        "dataset_id": REFERENCE["dataset_id"],
        "dataset_url": REFERENCE["dataset_url"],
        "sfc_reference_page": REFERENCE["sfc_reference_page"],
        "snapshot_sha256": digest,
        "snapshot_bytes": len(raw),
        "snapshot_downloaded_utc": REFERENCE["downloaded_utc"],
        "snapshot_rows": len(rows),
        "snapshot_distinct_dates": len(cut_dates),
        "snapshot_max_observation": max(cut_dates).isoformat(),
        "source_grain": "fecha_de_corte × nombre_patrimonio × descripcion_clase_inversion; query result already aggregated from Formato 351",
        "analysis_cut": selected_date.isoformat(),
        "source_fields_used": ["fecha_de_corte", "nombre_patrimonio", "descripcion_clase_inversion", "valor_mercado"],
        "source_rows_at_cut": len(selected),
        "source_zero_market_values_at_cut": sum(r["market_value"] == 0 for r in selected),
        "source_negative_market_values_at_cut": sum(r["market_value"] < 0 for r in selected),
        "portfolios_by_profile": {p: sorted(funds_by_profile[p]) for p in PROFILE_ORDER},
        "aggregation": "value-weighted profile composition sums market_value across source portfolio names within each official profile; equal-portfolio median is a sensitivity that treats absent class rows as zero",
        "profile_summary": profile_summary,
        "decision_use": "contextual reference for a human review of reported asset allocation by pension-fund profile; verifies source-to-weight aggregation only",
        "prohibited_inference": "does not validate return forecasts, expected returns, covariance, portfolio optimization, alpha, future risk, compliance, or suitability for any investor",
        "freshness_note": "The external snapshot was downloaded 2026-10-11 but its latest observation is 2026-07-31; it is a frozen historical cut, not a current portfolio view.",
    }
    (REPORTS / "observed_allocation_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    fig, ax = plt.subplots(figsize=(12.5, 8.3), constrained_layout=True)
    image = ax.imshow(heat, cmap="Blues", aspect="auto", vmin=0, vmax=65)
    ax.set_xticks(range(len(PROFILE_ORDER)), ["Conservador", "Moderado", "Mayor riesgo", "Retiro\nprogramado"])
    ax.set_yticks(range(len(heat_rows)), [short_class_label(c) for c in top_classes] + [other_label])
    ax.set_title("Composición observada de FPO por perfil\nCorte común: 31-jul-2026 · pesos sobre el valor de mercado reportado", loc="left", fontsize=14, weight="bold", pad=16)
    ax.set_xlabel("Perfil del patrimonio reportado por la SFC")
    ax.set_ylabel("Clase de inversión SFC (top 8 por valor; residual agrupado)")
    for i in range(heat.shape[0]):
        for j in range(heat.shape[1]):
            value = heat[i, j]
            ax.text(j, i, f"{value:.1f}%", ha="center", va="center", color="white" if value >= 34 else "#1f2937", fontsize=10, weight="bold" if value >= 20 else "normal")
    cbar = fig.colorbar(image, ax=ax, shrink=.8, pad=.025)
    cbar.set_label("Participación del valor de mercado (%)")
    fig.text(.01, -.015, "Ponderación agrupada por valor entre patrimonios reportados; no representa el fondo promedio ni el desempeño. Véanse clases completas y sensibilidad en el CSV.", fontsize=8)
    fig.savefig(REPORTS / "observed_allocation_heatmap.png", dpi=180, bbox_inches="tight")
    print(json.dumps({"cut": selected_date.isoformat(), "profiles": {p: {"funds": profile_summary[p]["n_reported_portfolios"], "total_cop": profile_summary[p]["total_market_value_cop"], "top3": profile_summary[p]["top_3_pooled_classes"]} for p in PROFILE_ORDER}, "source_sha256": digest}, ensure_ascii=False))


if __name__ == "__main__":
    main()
