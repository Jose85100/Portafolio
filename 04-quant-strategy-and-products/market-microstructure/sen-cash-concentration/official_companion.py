#!/usr/bin/env python3
"""Daily descriptive concentration proxy from BanRep's monthly SEN close summary."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import argparse
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parent
SOURCE_REFERENCE = ROOT / "data" / "source_reference.json"
REPORTS = ROOT / "reports"
EXPECTED_SOURCE_ROWS = 1294
EXPECTED_CASH_ROWS = 547


def read_source_bytes() -> tuple[bytes, str, dict]:
    reference = json.loads(SOURCE_REFERENCE.read_text(encoding="utf-8"))
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--source-zip", type=Path, help="ZIP del snapshot obtenido fuera del proyecto (por ejemplo, desde Master_DATOS).")
    source.add_argument("--download-source", action="store_true", help="Descarga expresamente el ZIP desde la URL oficial BanRep.")
    args = parser.parse_args()
    if args.download_source:
        request = Request(reference["official_url"], headers={"User-Agent": "Portafolio-SEN-companion/1.0"})
        with urlopen(request, timeout=45) as response:
            raw = response.read()
        retrieval = "descargado de la URL oficial BanRep por solicitud explícita"
    else:
        if not args.source_zip.is_file():
            raise FileNotFoundError(f"No existe el archivo indicado: {args.source_zip}")
        raw = args.source_zip.read_bytes()
        retrieval = "archivo de staging indicado por --source-zip; no se conserva ni duplica en el proyecto"
    digest = hashlib.sha256(raw).hexdigest()
    if digest != reference["sha256"]:
        raise ValueError(f"SHA-256 inesperado: {digest}; esperado {reference['sha256']} para el vintage congelado")
    return raw, retrieval, reference


def main() -> None:
    REPORTS.mkdir(exist_ok=True)
    raw, retrieval, reference = read_source_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        workbook_name = "ResumenCierresSeptiembre2026.xlsx"
        if workbook_name not in archive.namelist():
            raise ValueError(f"El zip no contiene {workbook_name}")
        workbook_bytes = archive.read(workbook_name)
    wb = load_workbook(io.BytesIO(workbook_bytes), read_only=True, data_only=True)
    if wb.sheetnames != ["Resumen"]:
        raise ValueError(f"Hojas inesperadas: {wb.sheetnames}")
    ws = wb["Resumen"]
    header = [str(v).replace("\n", " ").strip() if v is not None else "" for v in next(ws.iter_rows(min_row=7, max_row=7, values_only=True))]
    required = ["FECHA", "ESPECIE", "RUEDA", "PLAZO IDA", "PLAZO VUELTA", "VOLUMEN", "CANTIDAD", "CANTIDAD DE CIERRES"]
    if header[:8] != required:
        raise ValueError(f"Encabezados inesperados: {header[:8]}")

    rows = []
    for row in ws.iter_rows(min_row=8, values_only=True):
        if row[0] is None:
            continue
        date = datetime.strptime(str(row[0]), "%Y%m%d").date()
        species, wheel = str(row[1]).strip(), str(row[2]).strip()
        amount_pesos = float(row[6]) if row[6] is not None else None
        closes = int(row[7]) if row[7] is not None else None
        if not species or not wheel or amount_pesos is None or amount_pesos < 0 or closes is None or closes < 0:
            raise ValueError(f"Registro inválido: {row[:8]}")
        rows.append((date, species, wheel, str(row[3]).strip(), str(row[4]).strip(), amount_pesos, closes))
    wb.close()
    if len(rows) != EXPECTED_SOURCE_ROWS:
        raise ValueError(f"Filas observadas {len(rows)} != {EXPECTED_SOURCE_ROWS}")
    key = [(r[0], r[1], r[2], r[3], r[4]) for r in rows]
    if len(set(key)) != len(key):
        raise ValueError("Llave fuente FECHA×ESPECIE×RUEDA×PLAZO IDA×PLAZO VUELTA duplicada")

    # CONH is the SEN cash purchase/sale wheel settling on the same day.
    cash = [r for r in rows if r[2] == "CONH"]
    if len(cash) != EXPECTED_CASH_ROWS:
        raise ValueError(f"Filas CONH observadas {len(cash)} != {EXPECTED_CASH_ROWS}")
    by_day_species: dict[tuple, float] = defaultdict(float)
    for date, species, _wheel, _ida, _vuelta, amount, _closes in cash:
        by_day_species[(date, species)] += amount
    days = sorted({date for date, _species, *_ in cash})
    measures = []
    for date in days:
        species_values = {species: value for (d, species), value in by_day_species.items() if d == date}
        total = sum(species_values.values())
        if total <= 0:
            continue
        shares = {species: value / total for species, value in species_values.items()}
        hhi = 10_000 * sum(share * share for share in shares.values())
        top_species = max(shares, key=shares.get)
        measures.append({
            "date": date.isoformat(),
            "wheel": "CONH",
            "amount_cop": round(total),
            "amount_cop_billions": total / 1e9,
            "n_species": len(species_values),
            "hhi_0_10000": hhi,
            "effective_species_count": 10_000 / hhi,
            "top_species": top_species,
            "top_species_share_pct": 100 * shares[top_species],
        })
    if len(measures) != 22 or measures[0]["date"] != "2026-09-01" or measures[-1]["date"] != "2026-09-30":
        raise ValueError("Calendario de días de negociación inesperado")
    with (REPORTS / "sen_conh_daily_concentration.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(measures[0]))
        writer.writeheader()
        writer.writerows(measures)

    hhis = sorted(m["hhi_0_10000"] for m in measures)
    volumes = sorted(m["amount_cop"] for m in measures)
    median = lambda values: (values[(len(values) - 1) // 2] + values[len(values) // 2]) / 2
    summary = {
        "source": "Banco de la República, Resumen de cierres del Sistema Electrónico de Negociación (SEN), septiembre de 2026",
        "source_url": reference["official_url"],
        "source_page": "https://www.banrep.gov.co/es/sistemas-pago/sen/resumen-cierres",
        "canonical_drive_file_id": reference["drive_file_id"],
        "canonical_drive_url": reference["drive_url"],
        "canonical_drive_path": reference["master_drive_path"],
        "manifest_drive_file_id": reference["manifest_drive_file_id"],
        "retrieval_mode": retrieval,
        "source_consulted": "2026-11-10",
        "source_vintage": "2026-09; último día observado 2026-09-30",
        "source_grain": "date × security species × SEN trading wheel × ida term × return term; 1,294 rows",
        "source_rows": len(rows),
        "source_sha256": digest,
        "derived_population": "CONH only (same-day cash purchases/sales); 547 source rows, grouped to date × security species then aggregated by date",
        "derived_measure": "daily Herfindahl-Hirschman index = 10,000 × sum of squared security shares in CANTIDAD (COP) within CONH; effective species count = 10,000 / HHI",
        "days": len(measures),
        "cash_amount_total_cop": sum(m["amount_cop"] for m in measures),
        "daily_hhi_median": median(hhis),
        "daily_hhi_min": min(hhis),
        "daily_hhi_max": max(hhis),
        "daily_effective_species_count_median": median(sorted(m["effective_species_count"] for m in measures)),
        "daily_amount_cop_billions_median": median(volumes) / 1e9,
        "latest_date": measures[-1]["date"],
        "latest_hhi": measures[-1]["hhi_0_10000"],
        "publication_rights": "BanRep aviso legal permits reproduction of public statistical/economic information with source and consultation date; attribute and preserve source values. Derived calculations are clearly labeled as project transformations.",
        "decision_use": "descriptive monitoring of concentration in observed same-day SEN cash-trading activity; prompts human review when security concentration changes, not a measure of executable depth or portfolio liquidity",
    }
    (REPORTS / "sen_conh_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    dates = [datetime.fromisoformat(m["date"]) for m in measures]
    fig, axes = plt.subplots(2, 1, figsize=(11, 7.2), sharex=True, constrained_layout=True)
    axes[0].bar(dates, [m["amount_cop_billions"] for m in measures], color="#4C78A8", width=0.8)
    axes[0].set_title("Valor reportado en rueda CONH por día")
    axes[0].set_ylabel("COP miles de millones")
    axes[1].plot(dates, [m["hhi_0_10000"] for m in measures], color="#2A6F62", marker="o", lw=1.8, ms=4)
    axes[1].axhline(summary["daily_hhi_median"], color="#777777", ls="--", lw=1.2, label=f"Mediana del mes: {summary['daily_hhi_median']:.0f}")
    axes[1].set_title("Concentración diaria del valor por especie")
    axes[1].set_ylabel("HHI (0–10.000)")
    axes[1].set_xlabel("Fecha de negociación, septiembre de 2026")
    axes[1].legend(frameon=False)
    tick_dates = [datetime(2026, 9, day) for day in (1, 8, 15, 22, 30)]
    axes[1].set_xticks(tick_dates)
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    fig.suptitle("SEN BanRep | actividad observada en compraventas con cumplimiento el mismo día", fontsize=14, weight="bold")
    fig.text(.01, -.005, "Resumen agregado de cierres; HHI calculado sobre CANTIDAD en pesos. Un HHI mayor indica concentración del valor negociado entre menos especies.", fontsize=8)
    fig.savefig(REPORTS / "sen_conh_concentration.png", dpi=180, bbox_inches="tight")
    print(json.dumps({"rows": len(rows), "cash_rows": len(cash), "days": len(measures), "daily_hhi_median": summary["daily_hhi_median"], "latest_hhi": summary["latest_hhi"], "source_sha256": digest, "retrieval_mode": retrieval}, ensure_ascii=False))


if __name__ == "__main__":
    main()
