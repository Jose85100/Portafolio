#!/usr/bin/env python3
"""Build identifier-free aggregates from Supersociedades' public insolvency XLSX."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import ssl
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import certifi
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from openpyxl import load_workbook

SOURCE_URL = (
    "https://supersociedades.gov.co/documents/58444/9506465/"
    "Base-Soporte-Insolvencia-2026-CORTE-NOVIEMBRE.xlsx/"
    "5d402ff7-9bb8-a3a5-ca4e-e160c3847567?t=1793997727640&version=1.1"
)
EXPECTED_HEADERS = [
    "Nro", "NIT", "NOMBRE", "REGIONAL", "DEPARTAMENTO", "CIUDAD", "CIIU",
    "MACROSECTOR", "PROCESO", "CATEGORIA", "ACTIVO", "PASIVO", "EMPLEOS",
    "AÑO_DE_APERTURA_CELEBRACION", "FECHA AUTO ADMISION",
    "FECHA_REORGANIZACION_EN_EJECUCION", "DOCUMENTO FIRMA ACUERDO",
    "NÚMERO AUTO DE ADMISION", "FECHA DE GENERACIÓN",
]
OUT = Path(__file__).resolve().parent / "results"


def write_csv(path: Path, headers: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def number(value):
    if value is None or str(value).strip() == "":
        return None
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", help="Use a downloaded official XLSX; otherwise fetch it.")
    args = parser.parse_args()
    if args.xlsx:
        source = Path(args.xlsx).read_bytes()
    else:
        request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(
            request, context=ssl.create_default_context(cafile=certifi.where()), timeout=90
        ) as response:
            source = response.read()
    source_hash = hashlib.sha256(source).hexdigest()
    sheet = load_workbook(io.BytesIO(source), read_only=True, data_only=True).active
    iterator = sheet.iter_rows(values_only=True)
    headers = [str(x).strip() if x is not None else "" for x in next(iterator)]
    if headers != EXPECTED_HEADERS:
        raise SystemExit("Unexpected workbook schema; no outputs written.")

    proc = defaultdict(lambda: {"rows": 0, "asset_n": 0, "asset_sum": 0.0,
                                "liability_n": 0, "liability_sum": 0.0})
    sector = defaultdict(lambda: {"rows": 0, "asset_n": 0, "asset_sum": 0.0,
                                  "liability_n": 0, "liability_sum": 0.0})
    ids, missing_nro, duplicate_nro, rows_n = set(), 0, 0, 0
    bad_process = Counter()
    allowed_process = {
        "REORGANIZACIÓN EJECUCION", "LIQUIDACIÓN JUDICIAL EN TRAMITE",
        "REORGANIZACIÓN EN TRAMITE", "LIQUIDACIÓN JUDICIAL EJECUCION",
    }
    asset_missing = liability_missing = 0
    for row in iterator:
        if not row or all(v is None for v in row):
            continue
        rows_n += 1
        nro = str(row[0]).strip() if row[0] is not None else ""
        if not nro:
            missing_nro += 1
        elif nro in ids:
            duplicate_nro += 1
        else:
            ids.add(nro)
        process = str(row[8]).strip() if row[8] is not None else "SIN DATO"
        macro = str(row[7]).strip() if row[7] is not None else "SIN DATO"
        if process not in allowed_process:
            bad_process[process] += 1
        a, l = number(row[10]), number(row[11])
        if a is None: asset_missing += 1
        if l is None: liability_missing += 1
        for group, key in ((proc, process), (sector, macro)):
            item = group[key]
            item["rows"] += 1
            if a is not None:
                item["asset_n"] += 1; item["asset_sum"] += a
            if l is not None:
                item["liability_n"] += 1; item["liability_sum"] += l

    OUT.mkdir(exist_ok=True)
    def formatted(group):
        result = []
        for key, v in sorted(group.items(), key=lambda kv: (-kv[1]["rows"], kv[0])):
            result.append({
                "category": key, "records": v["rows"],
                "records_with_reported_assets": v["asset_n"],
                "reported_assets_sum_source_units": round(v["asset_sum"], 2),
                "records_with_reported_liabilities": v["liability_n"],
                "reported_liabilities_sum_source_units": round(v["liability_sum"], 2),
            })
        return result
    process_rows, sector_rows = formatted(proc), formatted(sector)
    write_csv(OUT / "by_process.csv", list(process_rows[0]), process_rows)
    write_csv(OUT / "by_macrosector.csv", list(sector_rows[0]), sector_rows)
    chart_rows = [r for r in process_rows if r["category"] in allowed_process]
    chart_rows.sort(key=lambda r: r["records"])
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.barh([r["category"].title() for r in chart_rows],
                   [r["records"] for r in chart_rows], color="#215a78")
    ax.bar_label(bars, padding=4, fmt="{:,.0f}")
    ax.set_xlabel("Registros en el corte publicado")
    ax.set_title("Inventario administrativo por proceso de insolvencia")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", alpha=.2)
    fig.tight_layout()
    fig.savefig(OUT / "records_by_process.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    summary = {
        "source": "Supersociedades Base de Datos Insolvencia, corte publicado 2026-11-06",
        "source_url": SOURCE_URL,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_sha256": source_hash,
        "records": rows_n,
        "unique_nro_in_memory": len(ids),
        "missing_nro": missing_nro,
        "duplicate_nro": duplicate_nro,
        "records_missing_assets": asset_missing,
        "records_missing_liabilities": liability_missing,
        "process_values_outside_expected_labels": dict(bad_process),
        "outputs_exclude_company_names_tax_ids_case_numbers_and_row_level_records": True,
        "interpretation": "Administrative inventory of records in insolvency procedures; not defaults, counterpart exposures, PD, LGD, EAD, recoveries, or loss outcomes.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest = {
        "source_sha256": source_hash,
        "output_sha256": {
            name: hashlib.sha256((OUT / name).read_bytes()).hexdigest()
            for name in ("by_process.csv", "by_macrosector.csv", "summary.json", "records_by_process.png")
        },
        "privacy": "No row-level identifiers or names are persisted.",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
