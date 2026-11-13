#!/usr/bin/env python3
"""Extract the SFC Aug-2026 IRL table as a separate, non-contiguous vintage."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import fitz  # PyMuPDF
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "data/raw/sfc_resultados_sistema_financiero_2026-08.pdf"
PAGE_URL = "https://www.superfinanciera.gov.co/publicaciones/10116287/resultados-del-sistema-financiero-colombiano-agosto-de-2026/"
PDF_URL = "https://www.superfinanciera.gov.co/loader.php?idFile=1083642&lFuncion=descargar&lServicio=Tools2&lTipo=descargas"
TABLE_URL = "https://www.superfinanciera.gov.co/publicaciones/60765/informes-y-cifrasinformesinforme-actualidad-del-sistema-financiero-colombiano-60765/"
PERIODS = {"ago.-25": "2025-08-31", "jul.-26": "2026-07-31", "ago.-26": "2026-08-31"}
ENTITY_ORDER = ["Bancos", "Compañías de Financiamiento", "Cooperativas Financieras", "Establecimientos de crédito"]
# Endpoint labels are the IRL values printed at the end of Gráfica 11 (page 20).
LATEST_CHART_LABELS_PCT = {
    "Bancos": 178.8,
    "Compañías de Financiamiento": 719.5,
    "Cooperativas Financieras": 238.2,
    "Establecimientos de crédito": 186.5,
}
LINE = re.compile(r"^(Bancos|Compañías de Financiamiento|Cooperativas Financieras|Establecimientos de crédito)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)$")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def millions(value: str) -> int:
    return int(value.replace(".", ""))


def main() -> None:
    if not PDF.exists():
        raise FileNotFoundError(PDF)
    doc = fitz.open(PDF)
    found = []
    text = ""
    page_index = None
    for i, page in enumerate(doc):
        page_text = page.get_text("text", sort=True)
        if ("Tabla 12. Componentes IRL" in page_text and "Gráfica 11. Evolución IRL" in page_text
                and "Tipo de entidad" in page_text and "RLN" in page_text):
            found.append(i)
            text, page_index = page_text, i
    if len(found) != 1:
        raise ValueError(f"Expected one IRL component table, found {len(found)}")
    doc.close()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    table_start = next(i for i, line in enumerate(lines) if "Tabla 12. Componentes IRL" in line)
    table_end = next(i for i, line in enumerate(lines[table_start + 1:], table_start + 1) if "Tabla 13. Componentes CFEN" in line)
    table_lines = lines[table_start:table_end]
    date_header = next((i for i, line in enumerate(table_lines)
                        if re.findall(r"(?:ago|jul)\.-\d{2}", line) == list(PERIODS)), None)
    if date_header is None:
        raise ValueError("The expected three SFC table dates were not found")
    matched = []
    for line in table_lines[date_header + 1:]:
        match = LINE.match(line)
        if match:
            matched.append((match.group(1), [millions(match.group(j)) for j in (2, 3, 4)]))
    if len(matched) != 8:
        raise ValueError(f"Expected 8 type rows (ALM/RLN), found {len(matched)}")
    if [name for name, _ in matched[:4]] != ENTITY_ORDER or [name for name, _ in matched[4:]] != ENTITY_ORDER:
        raise ValueError("SFC table row order changed; refusing to infer ALM/RLN mapping")

    alm_rows, rln_rows = matched[:4], matched[4:]
    records = []
    for idx, (label, period) in enumerate(PERIODS.items()):
        for (entity_type, alm_vals), (rln_type, rln_vals) in zip(alm_rows, rln_rows):
            if entity_type != rln_type:
                raise ValueError("Entity type mismatch between ALM and RLN table blocks")
            alm, rln = alm_vals[idx], rln_vals[idx]
            if rln <= 0:
                raise ValueError(f"Nonpositive RLN for {entity_type} {period}")
            records.append({
                "period": period, "source_period_label": label, "entity_type": entity_type,
                "alm_million_cop": alm, "rln_30d_million_cop": rln,
                "irl_ratio_calculated": alm / rln,
                "irl_pct_calculated": 100 * alm / rln,
                "data_status": "published component snapshot; not continuous monthly series",
            })
    data = pd.DataFrame(records)

    # The chart exposes its latest four endpoint labels, which provide a cross-check
    # against the ratios reconstructed from the table at Aug-2026.
    latest = data[data.period == "2026-08-31"].set_index("entity_type")
    chart_checks = {}
    for entity_type, chart_value in LATEST_CHART_LABELS_PCT.items():
        computed = float(latest.loc[entity_type, "irl_pct_calculated"])
        difference = computed - chart_value
        if abs(difference) > 0.051:
            raise ValueError(f"Chart/table IRL reconciliation failed for {entity_type}: {computed:.4f} vs {chart_value}")
        chart_checks[entity_type] = {"table_ratio_pct": computed, "chart_label_pct": chart_value, "difference_pp": difference}

    # Aggregate component check: totals may differ from the sum of displayed types
    # by up to COP 1 million due to rounding in the published table.
    aggregate_checks = {}
    for period in data.period.unique():
        cut = data[data.period == period].set_index("entity_type")
        detail = ["Bancos", "Compañías de Financiamiento", "Cooperativas Financieras"]
        aggregate_checks[period] = {
            "alm_total_minus_sum_types_million_cop": int(cut.loc["Establecimientos de crédito", "alm_million_cop"] - cut.loc[detail, "alm_million_cop"].sum()),
            "rln_total_minus_sum_types_million_cop": int(cut.loc["Establecimientos de crédito", "rln_30d_million_cop"] - cut.loc[detail, "rln_30d_million_cop"].sum()),
        }
        if abs(aggregate_checks[period]["alm_total_minus_sum_types_million_cop"]) > 1 or abs(aggregate_checks[period]["rln_total_minus_sum_types_million_cop"]) > 1:
            raise ValueError(f"Aggregate ALM/RLN mismatch exceeds rounding at {period}")

    out, figs = ROOT / "results", ROOT / "figures"
    out.mkdir(exist_ok=True)
    figs.mkdir(exist_ok=True)
    data.to_csv(out / "sfc_irl_bulletin_appendix.csv", index=False, float_format="%.8f")
    old = pd.read_csv(out / "sfc_irl_by_entity_type_month.csv")
    old["source"] = "SFC historical workbook (through 2022-12)"
    old["irl_pct_reconstructed_from_rounded_alm_rln"] = old["irl_pct_reported"]
    data_dates = data.assign(period=pd.to_datetime(data.period))
    bulletin = data_dates[["period", "entity_type", "irl_pct_calculated"]].rename(columns={"irl_pct_calculated": "irl_pct_reconstructed_from_rounded_alm_rln"})
    bulletin["source"] = "SFC August-2026 results bulletin, Table 12"
    combined = pd.concat([old[["period", "entity_type", "source", "irl_pct_reconstructed_from_rounded_alm_rln"]], bulletin], ignore_index=True)
    combined["period"] = pd.to_datetime(combined.period)

    palette = {"Bancos": "#146C94", "Compañías de Financiamiento": "#E07A3F", "Cooperativas Financieras": "#3A7D44", "Establecimientos de crédito": "#5C5C5C"}
    fig, ax = plt.subplots(figsize=(11, 5.8))
    old_part = combined[combined.source.str.startswith("SFC historical")]
    for entity_type, group in old_part.groupby("entity_type", sort=False):
        group = group.sort_values("period")
        ax.plot(group.period, group.irl_pct_reconstructed_from_rounded_alm_rln, label=f"{entity_type} · serie histórica", color=palette.get(entity_type, "#8055A2"), lw=1.8)
    new_part = combined[combined.source.str.startswith("SFC August")]
    markers = {"ago.-25": "o", "jul.-26": "s", "ago.-26": "D"}
    for entity_type, group in new_part.groupby("entity_type", sort=False):
        group = group.merge(data_dates[["period", "entity_type", "source_period_label"]], on=["period", "entity_type"], how="left")
        for label, points in group.groupby("source_period_label"):
            ax.scatter(points.period, points.irl_pct_reconstructed_from_rounded_alm_rln, marker=markers[label], s=55,
                       color=palette.get(entity_type, "#8055A2"), label=f"{entity_type} · boletín" if label == "ago.-26" else None, zorder=3)
    ax.axhline(100, color="#A33A3A", linestyle="--", lw=1.4, label="Mínimo regulatorio 100%")
    ax.axvspan(pd.Timestamp("2023-01-01"), pd.Timestamp("2025-01-01"), color="#777777", alpha=.08, label="Sin cortes mensuales en los snapshots usados")
    ax.set_title("IRL por tipo: serie histórica y tres cortes de boletín")
    ax.set_ylabel("IRL (%) · banda de 30 días")
    ax.set_xlabel("Corte reportado")
    ax.grid(axis="y", alpha=.25)
    ax.legend(frameon=False, fontsize=8, ncol=2)
    fig.text(.01, .01, "Puntos: ago-2025, jul-2026 y ago-2026. No hay interpolación; punto por tipo, no por entidad.", fontsize=8)
    fig.tight_layout(rect=(0, .04, 1, 1))
    fig.savefig(figs / "sfc_irl_history_plus_bulletin.png", dpi=170)
    plt.close(fig)

    manifest = {
        "source_page": PAGE_URL, "monthly_report_index": TABLE_URL, "source_pdf_url": PDF_URL,
        "snapshot": "data/raw/sfc_resultados_sistema_financiero_2026-08.pdf", "sha256": sha256(PDF),
        "report_vintage": "Agosto 2026", "report_page_number_1based": page_index + 1,
        "source_cui_f_as_of": "2026-09-25", "extraction_date": "2026-11-10",
        "source_table": "Tabla 12. Componentes IRL", "source_graph": "Gráfica 11. Evolución IRL",
        "source_grain": "entity type × three published cut dates; no individual entities",
        "periods": list(PERIODS.values()), "entity_types": ENTITY_ORDER,
        "observation_count": len(data), "expected_observation_count": 12,
        "dates_are_non_contiguous": True,
        "source_method": "PDF text extraction of ALM and RLN table; IRL reconstructed as ALM/RLN × 100.",
        "units": "ALM and RLN in COP millions; IRL ratio dimensionless, displayed as percent.",
        "latest_graph_ratio_cross_checks": chart_checks,
        "aggregate_component_rounding_checks": aggregate_checks,
        "disclaimer": "Addendum only. Do not connect these three cut dates as a continuous monthly series or overwrite the historical XLS snapshot through Dec-2022.",
        "limitations": [
            "The historical SFC XLS ends Dec-2022; this PDF contains only three later component snapshots, not the missing monthly series.",
            "The new bulletin is type-level, not entity-level; entity percentiles cannot be extended.",
            "IRL is a reported prudential coverage ratio, not cash shortfall or probability of illiquidity.",
            "CUIF values are subject to SFC review; the bulletin states figures through Sep-25-2026.",
        ],
    }
    (out / "bulletin_appendix_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    report = [
        "# Anexo de vintage posterior: IRL en boletín SFC agosto de 2026", "",
        "## Alcance de la actualización", "",
        "El archivo histórico XLS de IRL del supervisor termina en diciembre de 2022. El boletín SFC de resultados a agosto de 2026 publica una tabla más reciente con componentes ALM/RLN para tres cortes: agosto de 2025, julio de 2026 y agosto de 2026. Son snapshots de tipo de entidad, no una extensión mensual continua ni una actualización entity-level.", "",
        "El informe indica que las cifras CUIF están sujetas a revisión y reportadas hasta el 25 de septiembre de 2026. La extracción de este apéndice conserva la publicación de agosto de 2026; no reescribe el snapshot histórico 2020–22.", "",
        "## Método y conciliación", "",
        "Desde la Tabla 12 se extraen ALM y RLN en millones de pesos. Se calcula IRL (%) = 100 × ALM/RLN. Para los cuatro agregados en agosto de 2026, las razones calculadas redondean a una décima igual a las etiquetas finales de la Gráfica 11: bancos 178,8%; compañías de financiamiento 719,5%; cooperativas financieras 238,2%; establecimientos de crédito 186,5%. El detalle de conciliación está en el manifiesto.", "",
        "La suma por tipo y el total publicado difieren como máximo COP 1 millón por los redondeos visibles de la tabla. No se consideran faltantes ni se infieren valores de los tramos no publicados.", "",
        "## Observaciones nuevas", "",
        "| Corte | Tipo | ALM (millones COP) | RLN 30d (millones COP) | IRL calculado (%) |",
        "|---|---|---:|---:|---:|",
    ]
    for r in data.itertuples():
        report.append(f"| {r.source_period_label} | {r.entity_type} | {r.alm_million_cop:,} | {r.rln_30d_million_cop:,} | {r.irl_pct_calculated:.1f} |")
    report += [
        "", "## Lectura y límites", "",
        "Estos tres cortes permiten refrescar una referencia de cobertura agregada por tipo y comprobar consistencia entre componentes ALM/RLN y el gráfico publicado. No sirven para estimar cambios mensuales entre diciembre de 2022 y agosto de 2025, variabilidad interna de entidades, ni distribución entity-level. No interpolar, suavizar ni unir los puntos con la serie 2020–22 como si hubiera observaciones intermedias.",
        "El IRL es cobertura prudencial a 30 días; no es probabilidad de iliquidez, riesgo de cash shortfall, ni validación del laboratorio de primera ruptura. La medición de brecha corporativa requiere estados internos de flujos y obligaciones.", "",
        "## Fuente y reproducción", "",
        f"[Página SFC del informe agosto 2026]({PAGE_URL}); [índice de informes mensuales]({TABLE_URL}). PDF congelado en `{manifest['snapshot']}`, SHA-256 `{manifest['sha256']}`, página {page_index + 1}. Tabla 12, figura 11.",
        "Desde la carpeta `observed-sfc-irl`: `python3 scripts/build_sfc_irl_bulletin_appendix.py`. Requiere PyMuPDF (`fitz`), pandas y matplotlib; lee el PDF congelado, valida el orden de filas/fechas, rehace los ratios y compara el corte ago-2026 con las etiquetas del gráfico.", "",
        "![Serie original más puntos discontinuos del boletín](../figures/sfc_irl_history_plus_bulletin.png)", "",
    ]
    (out / "bulletin_appendix_report.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps({"snapshot_sha256": manifest["sha256"], "page": page_index + 1,
                      "periods": manifest["periods"], "observations": len(data),
                      "chart_checks": chart_checks, "aggregate_checks": aggregate_checks}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
