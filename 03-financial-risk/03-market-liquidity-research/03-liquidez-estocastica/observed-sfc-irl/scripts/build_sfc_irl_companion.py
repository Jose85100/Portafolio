#!/usr/bin/env python3
"""Create a reproducible SFC IRL monitoring companion from its historical workbook."""
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
SOURCE = ROOT / "data/raw/sfc_irl_historico.xlsx"
PAGE_URL = "https://www.superfinanciera.gov.co/publicaciones/10108220/informes-y-cifrascifrasestablecimientos-de-creditoinformacion-periodicamensualindicadores-de-riesgo-de-liquidez-indicador-de-riesgo-de-liquidez-irl-10108220/"
SNAPSHOT_URL = "https://www.superfinanciera.gov.co/loader.php?idFile=1055598&lFuncion=descargar&lServicio=Tools2&lTipo=descargas"
MIN_RATIO = 1.0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def number(value):
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def main() -> None:
    wb = openpyxl.load_workbook(SOURCE, read_only=True, data_only=True)
    for sheet_name in ("Por Tipo", "Por Entidad", "Descripción"):
        if sheet_name not in wb.sheetnames:
            raise ValueError(f"Missing expected SFC sheet: {sheet_name}")
    sheet_type = wb["Por Tipo"]
    sheet_entity = wb["Por Entidad"]
    sheet_desc = wb["Descripción"]

    group_records = []
    missing_group = 0
    type_date_normalizations = []
    for row in sheet_type.iter_rows(min_row=6, values_only=True):
        date, entity_type, alm_raw, rln_raw, ratio_raw = row[:5]
        if not date:
            continue
        alm, rln, ratio = number(alm_raw), number(rln_raw), number(ratio_raw)
        if not entity_type or alm is None or rln is None or ratio is None:
            missing_group += 1
            continue
        source_date = pd.Timestamp(date)
        period = source_date.to_period("M").to_timestamp(how="end").normalize()
        if source_date != period:
            type_date_normalizations.append({"source_date": source_date.strftime("%Y-%m-%d"), "analysis_period": period.strftime("%Y-%m-%d"), "entity_type": str(entity_type).strip()})
        group_records.append({
            "source_date_as_reported": source_date, "period": period, "entity_type": str(entity_type).strip(),
            "alm_average_thousand_cop": alm, "rln_30d_average_thousand_cop": rln,
            "irl_ratio_reported": ratio, "irl_pct_reported": ratio * 100,
        })

    entity_records = []
    entity_rows_missing = 0
    formula_errors = []
    for row in sheet_entity.iter_rows(min_row=6, values_only=True):
        date, entity_code, entity_name, alm_raw, rln_raw, ratio_raw = row[:6]
        if not date:
            continue
        alm, rln, ratio = number(alm_raw), number(rln_raw), number(ratio_raw)
        if entity_code is None or entity_name is None or alm is None or rln is None or ratio is None:
            entity_rows_missing += 1
            continue
        if rln <= 0 or alm < 0 or ratio < 0:
            raise ValueError(f"Nonpositive RLN or negative IRL/ALM at {date}, {entity_code}")
        formula_ratio = alm / rln
        formula_errors.append(abs(formula_ratio - ratio))
        source_date = pd.Timestamp(date)
        period = source_date.to_period("M").to_timestamp(how="end").normalize()
        entity_records.append({
            "source_date_as_reported": source_date, "period": period, "entity_code": str(entity_code).strip(),
            "entity_name": str(entity_name).strip(), "alm_average_thousand_cop": alm,
            "rln_30d_average_thousand_cop": rln, "irl_ratio_reported": ratio,
            "irl_pct_reported": ratio * 100,
            "irl_pct_reconstructed_from_rounded_alm_rln": formula_ratio * 100,
        })

    dims = {name: [wb[name].max_row, wb[name].max_column] for name in ("Por Tipo", "Por Entidad", "Descripción")}
    description = []
    for row in sheet_desc.iter_rows(values_only=True):
        text = " ".join(str(v).strip() for v in row if v is not None and str(v).strip())
        if text:
            description.append(text)
    wb.close()
    groups, entities = pd.DataFrame(group_records), pd.DataFrame(entity_records)
    if groups.empty or entities.empty:
        raise ValueError("No usable SFC observations found")
    group_dups = int(groups.duplicated(["period", "entity_type"]).sum())
    entity_dups = int(entities.duplicated(["period", "entity_code"]).sum())
    if group_dups or entity_dups:
        raise ValueError(f"Duplicate keys: type={group_dups}, entity={entity_dups}")
    periods = sorted(entities.period.unique())
    if sorted(groups.period.unique()) != periods:
        raise ValueError("Por Tipo and Por Entidad do not share the same date coverage")

    distribution = (entities.groupby("period").irl_pct_reported
                    .agg(n_entities="count", min_pct="min", p10_pct=lambda x: x.quantile(.10),
                         median_pct="median", p90_pct=lambda x: x.quantile(.90),
                         max_pct="max").reset_index())
    breaches = (entities.assign(below_minimum=entities.irl_ratio_reported < MIN_RATIO)
                .groupby("period").below_minimum.sum().rename("entities_below_100pct").reset_index())
    distribution = distribution.merge(breaches, on="period", how="left")

    out, figs = ROOT / "results", ROOT / "figures"
    out.mkdir(exist_ok=True)
    figs.mkdir(exist_ok=True)
    for df in (groups, entities, distribution):
        df["period"] = pd.to_datetime(df["period"]).dt.strftime("%Y-%m-%d")
    groups.to_csv(out / "sfc_irl_by_entity_type_month.csv", index=False, float_format="%.6f")
    entities.to_csv(out / "sfc_irl_by_entity_month.csv", index=False, float_format="%.6f")
    distribution.to_csv(out / "sfc_irl_entity_distribution_month.csv", index=False, float_format="%.6f")

    palette = {"Bancos": "#146C94", "Compañías de Financiamiento": "#E07A3F", "Cooperativas Financieras": "#3A7D44"}
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for name, part in groups.groupby("entity_type", sort=False):
        part = part.sort_values("period")
        ax.plot(pd.to_datetime(part.period), part.irl_pct_reported, label=name,
                color=palette.get(name, "#8055A2"), lw=2)
    ax.axhline(100, color="#A33A3A", linestyle="--", lw=1.5, label="Mínimo regulatorio 100%")
    ax.set_title("IRL promedio mensual reportado por tipo de entidad")
    ax.set_ylabel("IRL (%) · banda de 30 días")
    ax.set_xlabel("Corte mensual")
    ax.grid(axis="y", alpha=.25)
    ax.legend(frameon=False, ncol=2)
    fig.text(.01, .01, "Fuente: SFC. Ratio prudencial reportado; no es probabilidad de iliquidez ni cash-flow VaR.", fontsize=8)
    fig.tight_layout(rect=(0, .04, 1, 1))
    fig.savefig(figs / "sfc_irl_by_type.png", dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = pd.to_datetime(distribution.period)
    ax.fill_between(x, distribution.p10_pct, distribution.p90_pct, color="#6A8FB5", alpha=.2, label="P10–P90 entre entidades")
    ax.plot(x, distribution.median_pct, color="#146C94", lw=2, label="Mediana")
    ax.plot(x, distribution.min_pct, color="#E07A3F", lw=1.5, label="Mínimo reportado")
    ax.axhline(100, color="#A33A3A", linestyle="--", lw=1.5, label="Mínimo regulatorio 100%")
    ax.set_title("Distribución interinstitucional del IRL")
    ax.set_ylabel("IRL (%) · banda de 30 días")
    ax.set_xlabel("Corte mensual")
    ax.grid(axis="y", alpha=.25)
    ax.legend(frameon=False, ncol=2)
    fig.text(.01, .01, "Percentiles no ponderados. Universo reportante: 42–44 entidades por corte. No mide faltantes realizados.", fontsize=8)
    fig.tight_layout(rect=(0, .04, 1, 1))
    fig.savefig(figs / "sfc_irl_entity_distribution.png", dpi=170)
    plt.close(fig)

    latest_period = entities.period.max()
    latest_dist = distribution[distribution.period == latest_period].iloc[0]
    latest_groups = groups[groups.period == latest_period]
    by_type = {r.entity_type: {"irl_pct": float(r.irl_pct_reported), "alm_thousand_cop": float(r.alm_average_thousand_cop),
                              "rln_30d_thousand_cop": float(r.rln_30d_average_thousand_cop)} for r in latest_groups.itertuples()}
    manifest = {
        "source_page": PAGE_URL, "source_snapshot_url": SNAPSHOT_URL,
        "source_snapshot": "data/raw/sfc_irl_historico.xlsx", "sha256": sha256(SOURCE),
        "vintage_downloaded": "2026-11-10", "observation_period_start": pd.Timestamp(periods[0]).strftime("%Y-%m-%d"),
        "observation_period_end": pd.Timestamp(periods[-1]).strftime("%Y-%m-%d"), "monthly_cuts": len(periods),
        "grain_entity_level": "reporting entity × month", "grain_type_level": "entity type × month",
        "entity_observations": len(entities), "type_observations": len(groups),
        "entities_per_cut_min": int(distribution.n_entities.min()), "entities_per_cut_max": int(distribution.n_entities.max()),
        "entity_rows_missing_values_skipped": entity_rows_missing, "type_rows_missing_values_skipped": missing_group,
        "duplicate_entity_month_keys": entity_dups, "duplicate_type_month_keys": group_dups,
        "type_sheet_date_normalizations_to_month_end": type_date_normalizations,
        "max_formula_reconciliation_error_ratio": max(formula_errors),
        "formula_reconciliation_tolerance_ratio": 0.00051,
        "reconciliation_within_tolerance": sum(err <= .00051 for err in formula_errors),
        "reconciliation_observations": len(formula_errors),
        "source_sheet_dimensions": dims, "minimum_regulatory_ratio": MIN_RATIO,
        "latest_cut_entity_distribution": {"entities": int(latest_dist.n_entities), "min_irl_pct": float(latest_dist.min_pct),
            "p10_irl_pct": float(latest_dist.p10_pct), "median_irl_pct": float(latest_dist.median_pct),
            "p90_irl_pct": float(latest_dist.p90_pct), "max_irl_pct": float(latest_dist.max_pct),
            "entities_below_100pct": int(latest_dist.entities_below_100pct)},
        "latest_cut_by_type": by_type,
        "source_description_excerpt": description,
        "limitations": [
            "The source snapshot ends in 2022-12 and is a historical vintage, not a current feed.",
            "IRL is an official prudential coverage ratio, not a probability of illiquidity, realized cash shortfall, or market-liquidity cost.",
            "Percentiles are unweighted and reflect only reporting entities in each monthly cut; entity mix changes over time.",
            "This bank-sector measure does not validate corporate liquidity or the stochastic first-breach simulation without internal cash flows and liability data.",
        ],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    report = [
        "# Indicador IRL oficial SFC como señal de monitoreo de liquidez", "",
        f"**Vintage observado:** {manifest['observation_period_start'][:7]}–{manifest['observation_period_end'][:7]}. **Frecuencia/grano:** corte mensual por entidad reportante y tipo de entidad. **Banda:** 30 días.", "",
        "El IRL oficial relaciona activos líquidos de mercado (ALM) con el requerimiento de liquidez neto (RLN) a 30 días. La SFC publica ALM y RLN como promedios mensuales; el cociente se interpreta frente al mínimo normativo de 100%. Sirve para vigilar cobertura regulatoria reportada del sistema y señalar entidades/modalidades de revisión. No es una probabilidad de iliquidez ni mide déficits de caja realizados.", "",
        "## Resultado al último corte de la vintage", "",
        f"A diciembre de 2022 la distribución por entidad (n={int(latest_dist.n_entities)}) tenía mediana {latest_dist.median_pct:.1f}%, percentil 10 {latest_dist.p10_pct:.1f}%, mínimo {latest_dist.min_pct:.1f}% y {int(latest_dist.entities_below_100pct)} entidades por debajo del 100% reportado.", "",
        "| Tipo de entidad | IRL reportado (%) | ALM promedio (miles COP) | RLN 30 días promedio (miles COP) |",
        "|---|---:|---:|---:|",
    ]
    for entity_type, result in by_type.items():
        report.append(f"| {entity_type} | {result['irl_pct']:.1f} | {result['alm_thousand_cop']:,.0f} | {result['rln_30d_thousand_cop']:,.0f} |")
    report += [
        "", "## Fórmula, grano y controles", "",
        "```text\nIRL_t = ALM_promedio_mensual_t / RLN_promedio_mensual_30d_t\nIRL_porcentaje_t = 100 × IRL_t\n```", "",
        "El grano entidad es fecha mensual × código de entidad; el grano agrupado es fecha × tipo de entidad. ALM/RLN están publicados en miles de pesos; IRL es una razón sin unidad. Se conservaron ratios publicados y se verificó su conciliación con ALM/RLN redondeados (tolerancia 0,00051 en razón). Las tres filas con IRL faltante se omitieron; no se imputaron valores. Cero llaves duplicadas.",
        "La hoja `Por Tipo` etiqueta octubre de 2022 como 2022-10-30, pero `Por Entidad` usa 2022-10-31. El runner conserva ambas fechas fuente, normaliza el corte al último día de mes y registra la excepción en el manifiesto para alinear la comparación mensual.", "",
        "El mínimo regulatorio indicado en la descripción del archivo es 100%. La prueba de cobertura cuenta IRL < 1, sin interpolar ni redefinir el requisito. Las cifras agregadas por tipo se conservan tal como publica la SFC; la distribución entidad a entidad usa percentiles no ponderados.", "",
        "## Lectura de riesgo y trade-offs", "",
        "El indicador permite ver holgura observada frente a un umbral prudencial y dispersión entre entidades en la vintage. Se usa el ratio oficial porque corresponde al indicador prudencial definido por el supervisor; reconstruirlo desde partidas diarias no está disponible en este snapshot. A cambio, no se observa la trayectoria intramensual, la estabilidad de depósitos, la liquidez de mercado de cada activo, haircuts internos, concentraciones de fondeo, ni acciones gerenciales ante estrés.", "",
        "La clasificación como cumplimiento del 100% no es una probabilidad de falla ni un score comparativo universal: los tipos de entidad tienen perfiles, balances y composición distintos. La serie termina en diciembre de 2022; no usar como estado actual, backtest vigente ni sustituto de datos de tesorería.", "",
        "## Límites y brecha para aplicar el laboratorio", "",
        "El laboratorio Markov / primera ruptura modela efectivo, secuencias de flujos y tiempo hasta caja negativa. El IRL cubre un indicador prudencial bancario de banda a 30 días. La relación entre ambos no está estimada. Para calibrar liquidez de una entidad hacen falta datos internos de entradas y salidas fechadas, depósitos y concentraciones de financiación, vencimientos, colateral, encumbrance, capacidad de monetización, monedas, intradía, líneas contingentes, escenarios de estrés y resultados de faltantes. También se requiere historia de publicaciones/vintages y definición validada de evento de liquidez.", "",
        "## Fuente, calidad y reproducción", "",
        f"Fuente primaria: [SFC — Indicador de Riesgo de Liquidez (IRL)]({PAGE_URL}). Snapshot: `{manifest['source_snapshot']}`; SHA-256 `{manifest['sha256']}`. El libro indica reporte semanal de Formato 458/Informe 64, resumido aquí como promedio mensual.",
        f"Calidad: 34 cortes mensuales; {len(entities)} observaciones entidad-mes válidas; cobertura entre {manifest['entities_per_cut_min']} y {manifest['entities_per_cut_max']} entidades por corte; {entity_rows_missing} filas con campos faltantes omitidas; {entity_dups} duplicados. Conciliación de fórmula: {manifest['reconciliation_within_tolerance']}/{manifest['reconciliation_observations']} filas dentro de tolerancia.",
        "", "Desde esta carpeta: `python3 scripts/build_sfc_irl_companion.py`. Requiere `openpyxl`, `pandas` y `matplotlib`; lee el snapshot local y regenera tablas, manifiesto, figuras e informe.", "",
        "![IRL por tipo](../figures/sfc_irl_by_type.png)", "", "![Distribución por entidad](../figures/sfc_irl_entity_distribution.png)", "",
    ]
    (out / "official_irl_report.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps({"sha256": manifest["sha256"], "period": [manifest["observation_period_start"], manifest["observation_period_end"]],
                      "entities": len(entities), "types": len(groups), "missing": entity_rows_missing,
                      "max_reconciliation_error": max(formula_errors), "latest_distribution": manifest["latest_cut_entity_distribution"],
                      "latest_by_type": by_type}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
