#!/usr/bin/env python3
"""Build a descriptive SFC grade-mix shift companion from a frozen aggregate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data/sfc_product_risk_grade_mix_monthly.csv"
UPSTREAM_MANIFEST = ROOT / "data/upstream_manifest.json"
OUTPUT = ROOT / "results"
FIGURES = ROOT / "figures"
REQUIRED = {
    "fecha_corte", "unicap", "descrip_uc", "saldo_D_E",
    "saldo_calificado_A_E", "participacion_D_E_en_calificado_pct",
    "cobertura_calificacion_sobre_bruto_pct", "entidades_reportantes",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def build() -> None:
    df = pd.read_csv(INPUT)
    missing = sorted(REQUIRED - set(df.columns))
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")
    df["fecha_corte"] = pd.to_datetime(df["fecha_corte"], errors="coerce")
    if df["fecha_corte"].isna().any():
        raise ValueError("Hay fechas de corte inválidas")
    df["unicap"] = pd.to_numeric(df["unicap"], errors="coerce")
    for col in ("participacion_D_E_en_calificado_pct", "cobertura_calificacion_sobre_bruto_pct", "entidades_reportantes"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if df["unicap"].isna().any() or df["participacion_D_E_en_calificado_pct"].isna().any():
        raise ValueError("Hay claves de producto o participaciones no numéricas")
    if df.duplicated(["fecha_corte", "unicap"]).any():
        raise ValueError("La llave producto × fecha debe ser única")
    if not df["participacion_D_E_en_calificado_pct"].between(0, 100).all():
        raise ValueError("Participación D/E fuera de [0, 100]")

    # Compare a published product-level cross-section with the same product one
    # calendar year earlier. This is a mix shift, not account migration.
    df = df.sort_values(["unicap", "fecha_corte"]).copy()
    df["fecha_comparacion_12m"] = df["fecha_corte"] - pd.DateOffset(years=1)
    base = df[["fecha_corte", "unicap", "participacion_D_E_en_calificado_pct"]].rename(
        columns={"fecha_corte": "fecha_comparacion_12m", "participacion_D_E_en_calificado_pct": "participacion_D_E_12m_pct"}
    )
    out = df.merge(base, on=["fecha_comparacion_12m", "unicap"], how="left", validate="many_to_one")
    out["cambio_D_E_12m_pp"] = out["participacion_D_E_en_calificado_pct"] - out["participacion_D_E_12m_pct"]
    latest_date = out["fecha_corte"].max()
    latest = out.loc[out["fecha_corte"].eq(latest_date)].copy()
    latest = latest.sort_values("cambio_D_E_12m_pp", ascending=False, na_position="last")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    out["fecha_corte"] = out["fecha_corte"].dt.strftime("%Y-%m-%d")
    out["fecha_comparacion_12m"] = out["fecha_comparacion_12m"].dt.strftime("%Y-%m-%d")
    out.to_csv(OUTPUT / "sfc_product_grade_mix_shift.csv", index=False, float_format="%.6f")

    eligible = latest.dropna(subset=["cambio_D_E_12m_pp"])
    plot_data = eligible.head(6).sort_values("cambio_D_E_12m_pp")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    if len(plot_data):
        labels = [f"{int(row.unicap)} · {row.descrip_uc}" for row in plot_data.itertuples()]
        colors = ["#b42318" if value > 0 else "#26734d" for value in plot_data["cambio_D_E_12m_pp"]]
        ax.barh(labels, plot_data["cambio_D_E_12m_pp"], color=colors)
        ax.axvline(0, color="#333333", linewidth=0.8)
    ax.set_xlabel("Cambio anual en participación D+E (puntos porcentuales)")
    ax.set_title(f"Cambio de mezcla de calificación SFC · corte {latest_date:%Y-%m}")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "sfc-grade-mix-shift-latest.png", dpi=170)
    plt.close(fig)

    upstream = json.loads(UPSTREAM_MANIFEST.read_text(encoding="utf-8"))
    summary = {
        "latest_cut": latest_date.strftime("%Y-%m-%d"),
        "products_at_latest_cut": int(len(latest)),
        "products_with_12m_comparison": int(eligible.shape[0]),
        "largest_positive_12m_mix_shifts": [
            {
                "product_code": int(r.unicap),
                "product": r.descrip_uc,
                "share_de_latest_pct": round(float(r.participacion_D_E_en_calificado_pct), 4),
                "change_12m_pp": round(float(r.cambio_D_E_12m_pp), 4),
                "reporting_entities": int(r.entidades_reportantes),
                "coverage_pct": round(float(r.cobertura_calificacion_sobre_bruto_pct), 4),
            }
            for r in eligible.head(5).itertuples()
        ],
        "interpretation": "Descriptive change in product-level D+E grade mix; not account-level migration, default incidence, or a transition probability.",
    }
    (OUTPUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "source_dataset": "SFC rvii-eis8, Distribución de cartera por producto",
        "source_url": upstream["source"]["dataset_url"],
        "source_api_url": upstream["source"]["api_url"],
        "upstream_raw_sha256": upstream["source"]["raw_csv_sha256"],
        "upstream_retrieved_at_utc": upstream["source"]["api_retrieved_at_utc"],
        "upstream_cutoff": upstream["snapshot"]["last_cut"],
        "input_file": INPUT.name,
        "input_sha256": sha256(INPUT),
        "input_rows": int(len(df)),
        "input_products": int(df["unicap"].nunique()),
        "input_date_start": df["fecha_corte"].min().strftime("%Y-%m-%d"),
        "input_date_end": latest_date.strftime("%Y-%m-%d"),
        "output_latest_cut": summary["latest_cut"],
        "method": "Same-product difference in published D+E share against the calendar cut 12 months earlier; exact date match required.",
        "limits": [
            "Repeated aggregate snapshots do not track the same borrowers or accounts.",
            "D+E is an SFC risk-grade mix, not a universal default label or delinquency transition.",
            "Changes combine underlying performance, portfolio composition, reporting coverage, and entity mix.",
            "This descriptive signal does not estimate or validate a transition matrix or IFRS 9 PD.",
        ],
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Cambio observado de mezcla de calificación D+E por producto",
        "",
        f"**Corte más reciente:** {summary['latest_cut']}. **Productos:** {summary['products_at_latest_cut']}. **Comparaciones interanuales disponibles:** {summary['products_with_12m_comparison']}.",
        "",
        "Esta aplicación usa saldos agregados mensuales de calificación de riesgo A–E publicados por la SFC. Para cada producto compara la participación D+E del corte con el mismo producto y fecha calendario un año antes. El resultado sirve para priorizar revisión de mezcla sectorial.",
        "",
        "## Lectura y límites",
        "",
        "Una variación positiva significa que aumentó la parte de los saldos calificados A–E ubicada en D+E. No significa que cuentas hayan migrado individualmente desde A–C hacia D–E: los cortes agregados no enlazan prestatarios. La variación también responde a altas, bajas, amortización, castigos, composición y cambios en reportantes. D+E no se interpreta como default universal, PD, mora ni tasa de transición.",
        "",
        "El tablero es una referencia descriptiva para vigilancia de mezcla. No estima la matriz de transición del laboratorio ni valida una PD de originación o IFRS 9. Esa validación requiere panel por operación, identificador seudonimizado estable, estados de origen y destino, saldo, curas, cierres y default definido institucionalmente.",
        "",
        "![Cambio anual por producto](../figures/sfc-grade-mix-shift-latest.png)",
        "",
        "## Reproducción y linaje",
        "",
        "Desde este directorio, ejecutar `python3 build_companion.py` (requiere pandas y matplotlib). El snapshot agregado está en `data/`; el manifiesto registra hash del archivo, fuente y vintage del extracto SFC original. La transformación ascendente, campos y controles están descritos en el companion [SFC de mezcla de calificación por producto](../../../perdida-esperada-pd-lgd-ead/observed-sfc-product-risk-mix/README.md).",
        "",
        "Salidas: `results/sfc_product_grade_mix_shift.csv`, `results/summary.json`, `results/manifest.json` y la figura anterior.",
    ]
    (OUTPUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build()
