#!/usr/bin/env python3
"""Build an observed holder-category concentration companion from canonical XLSX."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import date, datetime
from pathlib import Path

import openpyxl
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


EXPECTED_SHA256 = "a900a98916e3dd8fd9242b4f776953201ead023b4ca3621d729e6247dc47a2ce"
ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def month_string(value) -> str:
    if isinstance(value, datetime):
        return value.strftime("%Y-%m")
    if isinstance(value, date):
        return value.strftime("%Y-%m")
    raise ValueError(f"Fecha mensual con formato inesperado: {value!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="Ruta al XLSX canónico de Master_DATOS/ATLAS_ECONOMICO_COLOMBIA/01_RAW")
    args = parser.parse_args()
    source = args.source.expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"No existe la fuente canónica: {source}")
    source_hash = sha256(source)
    if source_hash != EXPECTED_SHA256:
        raise SystemExit(f"Hash distinto al vintage documentado: {source_hash}")

    wb = openpyxl.load_workbook(source, data_only=True, read_only=False)
    if "Diciembre2025" not in wb.sheetnames:
        raise SystemExit(f"Hoja Diciembre2025 ausente; hojas disponibles: {wb.sheetnames}")
    ws = wb["Diciembre2025"]
    labels = [ws.cell(r, 1).value for r in range(14, 35)]
    if len(labels) != 21 or any(not isinstance(x, str) or not x.strip() for x in labels):
        raise SystemExit("Se esperaban 21 categorías con nombre en A14:A34")

    observations = []
    dates = []
    reconciliations = []
    for col in range(2, 194):
        month = month_string(ws.cell(12, col).value)
        if month in dates:
            raise SystemExit(f"Mes duplicado: {month}")
        dates.append(month)
        values = [ws.cell(r, col).value for r in range(14, 35)]
        total = ws.cell(35, col).value
        if not isinstance(total, (int, float)) or total <= 0:
            raise SystemExit(f"Total faltante/no positivo para {month}: {total!r}")
        if any(not isinstance(x, (int, float)) for x in values):
            raise SystemExit(f"Valor no numérico en categorías para {month}")
        values = [float(x) for x in values]
        if any(x < 0 for x in values):
            raise SystemExit(f"Valor negativo en categorías para {month}")
        total = float(total)
        err = abs(sum(values) - total) / total
        reconciliations.append(err)
        if err > 1e-10:
            raise SystemExit(f"Las categorías no concilian con total en {month}: error relativo {err}")
        shares = [x / total for x in values]
        ranked = sorted(shares, reverse=True)
        observations.append({
            "month": month,
            "total_millions_cop": total,
            "holder_categories": len(values),
            "hhi_0_10000": 10000 * sum(x * x for x in shares),
            "largest_category_share_pct": 100 * ranked[0],
            "top3_category_share_pct": 100 * sum(ranked[:3]),
        })

    if len(observations) != 192 or dates[0] != "2010-01" or dates[-1] != "2025-12":
        raise SystemExit(f"Cobertura inesperada: n={len(observations)}, {dates[0]}..{dates[-1]}")
    if any(a >= b for a, b in zip(dates, dates[1:])):
        raise SystemExit("Los meses no están en orden estricto")

    results = ROOT / "results"
    figures = ROOT / "figures"
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    csv_path = results / "tes_holder_concentration_monthly.csv"
    fields = list(observations[0])
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(observations)

    xs = [o["month"] for o in observations]
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    ax.plot(xs, [o["hhi_0_10000"] for o in observations], color="#165D8F", lw=2, label="HHI por categoría")
    ax.set_ylabel("HHI (0–10.000)")
    ax.set_xlabel("Corte mensual")
    ax.grid(axis="y", alpha=.25)
    tick_positions = list(range(0, len(xs), 12))
    ax.set_xticks(tick_positions, [xs[i][:4] for i in tick_positions])
    ax2 = ax.twinx()
    ax2.plot(xs, [o["top3_category_share_pct"] for o in observations], color="#C36A25", lw=1.6, alpha=.9, label="Participación top 3")
    ax2.set_ylabel("Participación de las tres categorías principales (%)")
    ax.set_title("Concentración de tenencias TES por categoría publicada")
    lines = ax.get_lines() + ax2.get_lines()
    ax.legend(lines, [x.get_label() for x in lines], loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(figures / "tes_holder_concentration.png", dpi=180)
    plt.close(fig)

    start, end = observations[0], observations[-1]
    manifest = {
        "source_file": "irc_tenedores_tes_historico.xlsx (canonical external input; not bundled)",
        "source_url": "https://www.irc.gov.co/deuda-publica/deuda-interna-gnc/tenedores-tes/2025/-/document_library/dpfm/view_file/3002586",
        "source_drive_file_id": "1VXxopmjxSdZf6JJxpZA6BFd0uiWXsnff",
        "source_modified_utc": "2026-10-08T17:13:12.970Z",
        "source_sheet": "Diciembre2025",
        "source_sha256": source_hash,
        "source_unit": "millions of COP",
        "grain": "published TES holder category x month",
        "period_start": start["month"],
        "period_end": end["month"],
        "months": len(observations),
        "categories": 21,
        "total_reconciliation_max_relative_error": max(reconciliations),
        "hhi_start": start["hhi_0_10000"],
        "hhi_end": end["hhi_0_10000"],
        "hhi_min": min(o["hhi_0_10000"] for o in observations),
        "hhi_max": max(o["hhi_0_10000"] for o in observations),
        "top3_start_pct": start["top3_category_share_pct"],
        "top3_end_pct": end["top3_category_share_pct"],
        "derived_csv_sha256": sha256(csv_path),
        "runner": "python3 scripts/build_companion.py --source /absolute/path/to/irc_tenedores_tes_historico.xlsx",
        "interpretation": "Descriptive holder-category concentration proxy; not market liquidity, executable depth, price impact, fire-sale loss, or causal evidence.",
    }
    (results / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = f"""# Resultados observados: concentración de tenedores TES

Fuente: [Histórico Evolución de Tenedores TES 2010–2025, portal IRC](https://www.irc.gov.co/deuda-publica/deuda-interna-gnc/tenedores-tes/2025/-/document_library/dpfm/view_file/3002586), archivada en Master_DATOS/ATLAS_ECONOMICO_COLOMBIA/01_RAW; archivo canónico `{source.name}`. Su SHA-256 es `{source_hash}`. La copia canónica en Drive fue modificada el 8 de octubre de 2026; la hoja `Diciembre2025` contiene valores mensuales en millones de COP.

La serie tiene **192 meses** (2010-01 a 2025-12) y **21 categorías publicadas**. Las categorías suman el total general en todos los cortes; el máximo error relativo de conciliación fue {max(reconciliations):.3g}. No hay meses duplicados ni valores categóricos negativos o faltantes.

El HHI descriptivo por categoría pasó de **{start['hhi_0_10000']:.1f}** a **{end['hhi_0_10000']:.1f}** puntos. En diciembre de 2025, las tres categorías con mayores tenencias representaban **{end['top3_category_share_pct']:.1f}%** del total. El HHI observado varió entre {manifest['hhi_min']:.1f} y {manifest['hhi_max']:.1f} durante la ventana.

Estos resultados describen concentración agregada por las categorías de tenedor publicadas. No observan tenedores finales dentro de cada categoría, valores individuales, posiciones comprometidas, intención o sincronía de venta, transacciones, spreads, profundidad, volumen ejecutable ni respuesta de precios. Por tanto, son un **proxy estructural de concentración del universo tenedor**, útil para orientar preguntas de vigilancia y requerimientos de granularidad; no validan una espiral de ventas, no estiman impacto `λ`, no representan liquidez de mercado y no respaldan atribuciones causales.

El CSV derivado, la figura y la metadata de fuente/conciliación quedan en esta carpeta; no se incluye una copia del XLSX crudo.
"""
    (results / "report.md").write_text(report, encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
