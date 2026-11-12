#!/usr/bin/env python3
"""Build an aggregate SFC product/risk-grade companion from rvii-eis8."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATASET_ID = "rvii-eis8"
API_URL = "https://www.datos.gov.co/resource/rvii-eis8.csv?$limit=200000"
DATASET_URL = "https://www.datos.gov.co/en/en/Public-Finance/Distribuci-n-de-cartera-por-producto/rvii-eis8"
METADATA_URL = "https://www.datos.gov.co/api/views/rvii-eis8.json"
DRIVE_RAW_ID = "1FcdcUTlIHhV92TN8pEikcz0DX0896HBW"
DRIVE_RAW_PATH = (
    "Master_DATOS/04_SHADOW_RISK/01_RAW/01_RAW/2026-10-02_respaldo_local_pesados/"
    "docs/macro_2026_data/sfc_datasets/rvii-eis8.csv.gz"
)
GROSS = "_1_saldo_de_la_cartera_a"
GRADE_BALANCES = {
    "A": "_18_calificaci_n_de_riesgo",
    "B": "_20_calificaci_n_de_riesgo",
    "C": "_22_calificaci_n_de_riesgo",
    "D": "_24_calificaci_n_de_riesgo",
    "E": "_26_calificaci_n_de_riesgo",
}
KEY = ["fecha_corte", "tipo_entidad", "codigo_entidad", "unicap", "renglon"]
SELECTED_PRODUCTS = [1, 3, 7, 21]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def get_source(input_path: Path | None) -> tuple[Path, tempfile.TemporaryDirectory | None]:
    if input_path:
        if not input_path.is_file():
            raise FileNotFoundError(input_path)
        return input_path, None
    temp = tempfile.TemporaryDirectory(prefix="sfc-rvii-eis8-")
    target = Path(temp.name) / "rvii-eis8.csv"
    subprocess.run(["curl", "-fLsS", "--retry", "2", API_URL, "-o", str(target)], check=True)
    return target, temp


def build(source: Path) -> None:
    df = pd.read_csv(source, low_memory=False)
    required = set(KEY + ["descrip_uc", GROSS] + list(GRADE_BALANCES.values()))
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Schema incompleto; faltan columnas: {missing}")

    source_rows, source_cols = df.shape
    null_cells = int(df.isna().sum().sum())
    duplicate_key_rows = int(df.duplicated(KEY, keep=False).sum())
    exact_duplicate_rows = int(df.duplicated(keep=False).sum())
    all_dates = pd.to_datetime(df["fecha_corte"], errors="coerce")
    if all_dates.isna().any():
        raise ValueError("Hay fechas de corte inválidas")

    # renglon=5 is the product-total line. Other lines are product subtypes;
    # summing both would double count.
    prod = df.loc[pd.to_numeric(df["renglon"], errors="coerce").eq(5)].copy()
    for col in [GROSS] + list(GRADE_BALANCES.values()):
        prod[col] = pd.to_numeric(prod[col], errors="coerce")
    if prod[[GROSS] + list(GRADE_BALANCES.values())].isna().any().any():
        raise ValueError("Hay valores nulos/no numéricos en saldos usados")
    product_key_dups = int(prod.duplicated(KEY, keep=False).sum())
    if product_key_dups:
        raise ValueError(f"Llave de detalle duplicada tras filtro renglon=5: {product_key_dups}")

    prod["fecha_corte"] = pd.to_datetime(prod["fecha_corte"]).dt.strftime("%Y-%m-%d")
    prod["entidad_uid"] = prod["tipo_entidad"].astype(str) + ":" + prod["codigo_entidad"].astype(str)
    prod["calificaciones_A_E"] = prod[list(GRADE_BALANCES.values())].sum(axis=1)
    prod["calificaciones_D_E"] = prod[GRADE_BALANCES["D"]] + prod[GRADE_BALANCES["E"]]
    grouped = prod.groupby(["fecha_corte", "unicap", "descrip_uc"], as_index=False).agg(
        saldo_bruto=(GROSS, "sum"),
        saldo_A=(GRADE_BALANCES["A"], "sum"),
        saldo_B=(GRADE_BALANCES["B"], "sum"),
        saldo_C=(GRADE_BALANCES["C"], "sum"),
        saldo_D=(GRADE_BALANCES["D"], "sum"),
        saldo_E=(GRADE_BALANCES["E"], "sum"),
        entidades_reportantes=("entidad_uid", "nunique"),
        filas_entidad=("codigo_entidad", "size"),
    )
    grouped["saldo_calificado_A_E"] = grouped[["saldo_A", "saldo_B", "saldo_C", "saldo_D", "saldo_E"]].sum(axis=1)
    grouped["saldo_D_E"] = grouped["saldo_D"] + grouped["saldo_E"]
    grouped["participacion_D_E_en_calificado_pct"] = (
        100 * grouped["saldo_D_E"] / grouped["saldo_calificado_A_E"].replace(0, pd.NA)
    )
    grouped["cobertura_calificacion_sobre_bruto_pct"] = (
        100 * grouped["saldo_calificado_A_E"] / grouped["saldo_bruto"].replace(0, pd.NA)
    )
    grouped = grouped.sort_values(["unicap", "fecha_corte"]).reset_index(drop=True)

    if grouped.duplicated(["fecha_corte", "unicap"]).any():
        raise ValueError("El derivado no es único por fecha y producto")

    out_data = ROOT / "data/processed/sfc_product_risk_grade_mix_monthly.csv"
    out_data.parent.mkdir(parents=True, exist_ok=True)
    grouped.to_csv(out_data, index=False, float_format="%.8f")

    # Select only lines whose rated-balance coverage is >=95% at every observed cut.
    coverage_floor = grouped.groupby("unicap")["cobertura_calificacion_sobre_bruto_pct"].min()
    if any(coverage_floor.get(code, 0) < 95 for code in SELECTED_PRODUCTS):
        raise ValueError("Producto seleccionado con cobertura histórica menor a 95%; revisar set de figuras")
    draw_figure(grouped)

    zero_gross = int((prod[GROSS] == 0).sum())
    negative_grade_cells = int((prod[list(GRADE_BALANCES.values())] < 0).sum().sum())
    cov = grouped["cobertura_calificacion_sobre_bruto_pct"].dropna()
    rounded_coverage = ((cov >= 98) & (cov <= 102)).mean()
    max_date = grouped["fecha_corte"].max()
    min_date = grouped["fecha_corte"].min()
    fetched_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest = {
        "source": {
            "dataset_id": DATASET_ID,
            "title": "Distribución de cartera por producto",
            "publisher": "Superintendencia Financiera de Colombia (SFC)",
            "dataset_url": DATASET_URL,
            "api_url": API_URL,
            "metadata_url": METADATA_URL,
            "official_description": "Saldo mensual por entidad, modalidad, producto, altura de mora y calificación de riesgo.",
            "canonical_drive_file_id": DRIVE_RAW_ID,
            "canonical_drive_path": DRIVE_RAW_PATH,
            "drive_raw_is_not_copied_into_repository": True,
            "api_retrieved_at_utc": fetched_at,
            "socrata_rows_updated_at_utc": "2026-10-23T14:57:52Z (metadata observed 2026-11-10)",
            "raw_csv_sha256": sha256(source),
            "raw_csv_bytes": source.stat().st_size,
            "raw_file_integrity_note": "Hash identifies the exact CSV input used for this build. The archived Drive gzip was not byte-compared; this does not assert byte identity with that archive.",
        },
        "snapshot": {
            "source_rows": source_rows,
            "source_columns": source_cols,
            "rows_after_product_total_filter_renglon_5": int(len(prod)),
            "derived_rows": int(len(grouped)),
            "products": int(grouped["unicap"].nunique()),
            "monthly_cuts": int(grouped["fecha_corte"].nunique()),
            "first_cut": min_date,
            "last_cut": max_date,
            "null_cells_source": null_cells,
            "duplicate_detail_key_rows_source": duplicate_key_rows,
            "exact_duplicate_rows_source": exact_duplicate_rows,
            "duplicate_product_total_key_rows": product_key_dups,
            "zero_gross_entity_product_month_rows": zero_gross,
            "negative_grade_balance_cells": negative_grade_cells,
            "share_product_month_coverage_98_to_102_pct": round(100 * float(rounded_coverage), 2),
            "derived_csv_sha256": sha256(out_data),
            "derived_csv_bytes": out_data.stat().st_size,
        },
        "grain": "One row per reporting month × SFC product/modality code (unicap), aggregated by summing reporting-entity product-total lines (renglon=5).",
        "transformations": {
            "product_total_filter": "renglon == 5; excludes lower-level product lines to prevent double counting.",
            "main_proxy": "100 × (saldo_D + saldo_E) / (saldo_A + saldo_B + saldo_C + saldo_D + saldo_E).",
            "coverage_guardrail": "100 × (saldo_A + ... + saldo_E) / saldo_bruto.",
            "auxiliary": "Raw aggregate balances by A-E, gross balance, number of reporting entities, and source rows are retained in the derived CSV.",
            "delinquency_bands": "Not used; overlapping delinquency-height columns are excluded.",
            "amount_units": "Source balances are kept in source units; no currency/unit conversion is applied. Ratios are unit invariant.",
        },
        "interpretation": {
            "claim": "Descriptive portfolio mix proxy: the share of balances assigned to SFC risk grades D or E among balances assigned any A-E grade, by product and month.",
            "not_validated": ["account-level probability of default", "default transition or roll rate", "LGD, EAD or expected loss", "origination scorecard", "provision adequacy", "causal effect or future loss"],
            "comparability": "Use within-product historical monitoring only. Product definitions, rating practices, reporting entities and their mix can vary over time and across products; the ratios are not directly rank-comparable across modalities.",
            "denominator": "Rated balance A-E, not gross balance. The separate coverage field shows rated balance divided by gross balance; where it is materially below 100%, the proxy covers only a subset of gross portfolio.",
            "integrity": "The raw hash binds this build to its exact input. The Drive canonical file ID/path are recorded for lineage. At runtime the script also validates schema, the composite detail key, numeric saldos, and uniqueness of the derived month-product grain. Drive archive byte equality is not claimed.",
        },
    }
    out_manifest = ROOT / "results/manifest.json"
    out_manifest.parent.mkdir(parents=True, exist_ok=True)
    out_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(grouped, manifest)
    print(f"Dataset: {source_rows:,} × {source_cols}; filas renglon=5: {len(prod):,}")
    print(f"Derivado: {len(grouped):,} filas, {grouped.unicap.nunique()} productos, {grouped.fecha_corte.nunique()} cortes ({min_date} a {max_date})")
    print(f"SHA-256 raw: {manifest['source']['raw_csv_sha256']}")
    print(f"Cobertura A-E dentro de 98–102%: {manifest['snapshot']['share_product_month_coverage_98_to_102_pct']:.2f}% de producto-mes")
    print(f"Salida: {out_data.relative_to(ROOT)}")


def draw_figure(data: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), sharex=True)
    labels = {1: "Crédito rotativo", 3: "Libre inversión", 7: "Microcrédito ≤25 SMMLV", 21: "Comercial PYMES"}
    for ax, code in zip(axes.flat, SELECTED_PRODUCTS):
        d = data.loc[data.unicap.eq(code)].copy()
        d["fecha_corte"] = pd.to_datetime(d["fecha_corte"])
        ax.plot(d.fecha_corte, d.participacion_D_E_en_calificado_pct, color="#a33232", linewidth=1.8, label="D+E / saldo calificado A–E")
        ax.set_title(f"{code} · {labels[code]}", loc="left", fontsize=10, fontweight="bold")
        ax.set_ylabel("D+E del saldo calificado (%)")
        ax.grid(alpha=0.25)
        ax2 = ax.twinx()
        ax2.plot(d.fecha_corte, d.cobertura_calificacion_sobre_bruto_pct, color="#326a8a", linewidth=1.2, alpha=.8, label="Cobertura A–E / bruto")
        ax2.set_ylabel("Cobertura A–E sobre bruto (%)", color="#326a8a", fontsize=8)
        ax2.tick_params(axis="y", labelcolor="#326a8a", labelsize=8)
    fig.suptitle("Mezcla agregada de calificación SFC por producto", fontsize=15, fontweight="bold")
    fig.text(.5, .01, "Serie descriptiva; proporción D+E entre saldo calificado. Cobertura sobre saldo bruto en eje derecho. No es PD ni transición.", ha="center", fontsize=9)
    fig.tight_layout(rect=[0, .04, 1, .94])
    target = ROOT / "figures/sfc_product_risk_grade_mix_selected_products.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=180, bbox_inches="tight")
    plt.close(fig)


def write_report(data: pd.DataFrame, manifest: dict) -> None:
    x = data.copy()
    x["fecha_corte"] = pd.to_datetime(x.fecha_corte)
    latest = x.fecha_corte.max()
    prior = latest - pd.DateOffset(years=1)
    lines = [
        "# Resultado observado — mezcla de calificación por producto",
        "",
        f"Corte más reciente: **{latest:%Y-%m-%d}**. Ventana disponible: {x.fecha_corte.min():%Y-%m-%d} a {latest:%Y-%m-%d}.",
        "",
        "El indicador principal es participación del saldo calificado D+E dentro del saldo calificado A–E. Se muestra junto a la cobertura A–E respecto del saldo bruto para hacer visible el denominador faltante.",
        "",
        "## Cortes seleccionados",
        "",
        "| Producto | D+E / saldo A–E (%) | Cobertura A–E / bruto (%) | Cambio interanual (pp) | Entidades reportantes |",
        "|---|---:|---:|---:|---:|",
    ]
    for code in SELECTED_PRODUCTS:
        d = x[x.unicap.eq(code)]
        now = d[d.fecha_corte.eq(latest)]
        old = d[d.fecha_corte.eq(prior)]
        if len(now) == 0:
            continue
        a = now.iloc[0]
        yoy = (a.participacion_D_E_en_calificado_pct - old.iloc[0].participacion_D_E_en_calificado_pct) if len(old) else float("nan")
        lines.append(f"| {a.descrip_uc} | {a.participacion_D_E_en_calificado_pct:.2f} | {a.cobertura_calificacion_sobre_bruto_pct:.2f} | {yoy:+.2f} | {int(a.entidades_reportantes)} |")
    snap = manifest["snapshot"]
    lines += [
        "",
        "## Calidad y lectura",
        "",
        f"- El archivo de entrada tiene {snap['source_rows']:,} filas y {manifest['source']['raw_csv_bytes']:,} bytes; el filtro `renglon=5` conserva {snap['rows_after_product_total_filter_renglon_5']:,} totales de producto.",
        f"- La llave de detalle `{', '.join(KEY)}` no tiene filas duplicadas en este vintage; el derivado contiene {snap['derived_rows']:,} filas únicas en grano mes × producto, {snap['products']} productos y {snap['monthly_cuts']} cortes.",
        f"- {snap['share_product_month_coverage_98_to_102_pct']:.2f}% de las observaciones producto-mes tienen cobertura A–E entre 98% y 102%. Hay {snap['zero_gross_entity_product_month_rows']:,} filas entidad-producto-mes con saldo bruto cero, excluidas de la interpretación de cobertura (no se eliminan del derivado).",
        "- La figura limita la lectura a cuatro productos con cobertura histórica mínima de 95%; sigue mostrando cobertura en el eje derecho. La selección no vuelve comparables las modalidades.",
        "- Los datos están agregados por entidad, modalidad/producto y corte; no contienen observaciones longitudinales de créditos individuales.",
        "",
        "## Interpretación y límites",
        "",
        "La serie sirve como **proxy descriptivo de mezcla de saldos clasificados en D/E** dentro de cada producto. Se puede usar para exploración, vigilancia sectorial y formular preguntas de análisis más detallado. Cambios pueden reflejar riesgo subyacente, pero también cambios de entidades reportantes, composición de cartera, reglas de calificación o cobertura.",
        "",
        "No mide probabilidad de incumplimiento, migraciones A→E, roll-rates, pérdida, mora contractual ni suficiencia de provisiones. No valida una PD de originación ni alimenta decisiones de aprobación, precio, límite o provisión. La ausencia de ID de crédito impide construir transiciones: dos cortes agregados no identifican quién migró de categoría.",
        "",
        "Los saldos D/E y A–E se agregan entre reportantes antes de calcular la proporción. En consecuencia, el cambio en la participación de entidades puede alterar el indicador. No se interpreta una diferencia entre productos como una diferencia de riesgo calibrada; sus poblaciones, escalas y prácticas de calificación pueden variar.",
        "",
        "## Integridad y linaje",
        "",
        f"- Dataset oficial SFC `{DATASET_ID}`; vintage descargado {manifest['source']['api_retrieved_at_utc']} UTC, última actualización de metadata observada {manifest['source']['socrata_rows_updated_at_utc']}.",
        f"- SHA-256 del CSV exacto de entrada: `{manifest['source']['raw_csv_sha256']}`. El hash identifica el archivo usado en este build; el snapshot comprimido canónico de Drive queda referenciado por ID `{DRIVE_RAW_ID}` y no se afirma igualdad byte a byte.",
        f"- SHA-256 del derivado agregado: `{manifest['snapshot']['derived_csv_sha256']}` ({manifest['snapshot']['derived_csv_bytes']:,} bytes).",
        "- El script valida columnas requeridas, fechas, saldos numéricos, llave entidad×producto×corte y unicidad mes×producto. Los datos crudos permanecen en Drive; este repositorio guarda el derivado agregado.",
        "",
        "El informe y la figura son descriptivos. Consultar `manifest.json` para métricas completas de calidad y transformación.",
    ]
    target = ROOT / "results/official_report.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="CSV local del dataset rvii-eis8; evita acceso a red.")
    args = parser.parse_args()
    source, temp = get_source(args.input)
    try:
        build(source)
    finally:
        if temp:
            temp.cleanup()


if __name__ == "__main__":
    main()
