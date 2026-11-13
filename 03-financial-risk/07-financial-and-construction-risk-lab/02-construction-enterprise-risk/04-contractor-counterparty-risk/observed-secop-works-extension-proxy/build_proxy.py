#!/usr/bin/env python3
"""Rebuild aggregate execution-extension indicators from an official SECOP II snapshot."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "results"
API = "https://www.datos.gov.co/resource/jbjy-vk9h.json"
YEARS = list(range(2020, 2026))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch(query: dict[str, str]) -> list[dict]:
    url = API + "?" + urlencode(query)
    request = Request(url, headers={"User-Agent": "portfolio-observed-data-proxy/1.0"})
    with urlopen(request, timeout=60) as response:
        if response.status != 200:
            raise RuntimeError(f"SECOP API status {response.status}")
        payload = json.load(response)
    if not isinstance(payload, list):
        raise ValueError("Unexpected API response; expected JSON array")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Re-query official Socrata API and replace aggregate snapshots")
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    all_query = {
        "$select": "date_extract_y(fecha_de_firma) as anio,count(*) as contratos,sum(dias_adicionados) as dias_extendidos",
        "$where": "tipo_de_contrato='Obra' AND fecha_de_firma >= '2020-01-01T00:00:00' AND fecha_de_firma < '2026-01-01T00:00:00'",
        "$group": "anio", "$order": "anio",
    }
    extended_query = {
        "$select": "date_extract_y(fecha_de_firma) as anio,count(*) as contratos_con_extension,sum(dias_adicionados) as dias_extendidos",
        "$where": "tipo_de_contrato='Obra' AND fecha_de_firma >= '2020-01-01T00:00:00' AND fecha_de_firma < '2026-01-01T00:00:00' AND dias_adicionados > 0",
        "$group": "anio", "$order": "anio",
    }
    files = {"all": RAW / "contracts_by_signature_year.json", "extended": RAW / "extended_contracts_by_signature_year.json"}
    if args.refresh:
        for key, query in (("all", all_query), ("extended", extended_query)):
            payload = fetch(query)
            files[key].write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for path in files.values():
        if not path.is_file():
            raise FileNotFoundError(f"Missing aggregate snapshot {path}; use --refresh to query SECOP")
    all_rows = json.loads(files["all"].read_text(encoding="utf-8"))
    extended_rows = json.loads(files["extended"].read_text(encoding="utf-8"))
    all_by_year = {int(row["anio"]): row for row in all_rows}
    extended_by_year = {int(row["anio"]): row for row in extended_rows}
    if set(all_by_year) != set(YEARS) or not set(extended_by_year).issubset(YEARS):
        raise ValueError("Annual grouping does not cover the declared 2020–2025 period")

    rows = []
    for year in YEARS:
        total = int(all_by_year[year]["contratos"])
        days_all = int(float(all_by_year[year].get("dias_extendidos") or 0))
        ext = int(extended_by_year.get(year, {}).get("contratos_con_extension", 0))
        days_ext = int(float(extended_by_year.get(year, {}).get("dias_extendidos") or 0))
        if ext > total or days_all != days_ext:
            raise ValueError(f"Aggregate mismatch for {year}: total={total}, extended={ext}, days={days_all}/{days_ext}")
        rows.append({"signature_year": year, "works_contracts": total, "contracts_with_positive_extension_days": ext,
                     "share_with_positive_extension_days": ext / total if total else None,
                     "extension_days_total": days_all,
                     "extension_days_per_all_contracts": days_all / total if total else None,
                     "extension_days_per_extended_contract": days_ext / ext if ext else None})

    csv_path = OUT / "annual_works_extension_proxy.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        stream.write("signature_year,works_contracts,contracts_with_positive_extension_days,share_with_positive_extension_days,extension_days_total,extension_days_per_all_contracts,extension_days_per_extended_contract\n")
        for row in rows:
            stream.write(f"{row['signature_year']},{row['works_contracts']},{row['contracts_with_positive_extension_days']},{row['share_with_positive_extension_days']:.8f},{row['extension_days_total']},{row['extension_days_per_all_contracts']:.6f},{row['extension_days_per_extended_contract']:.6f}\n")

    all_contracts = sum(row["works_contracts"] for row in rows)
    ext_contracts = sum(row["contracts_with_positive_extension_days"] for row in rows)
    metadata = {
        "provider": "Agencia Nacional de Contratación Pública - Colombia Compra Eficiente",
        "dataset": "SECOP II - Contratos Electrónicos", "dataset_id": "jbjy-vk9h", "api": API,
        "extracted_on": "2026-11-11", "source_last_updated": "2026-11-11 (Socrata metadata rowsUpdatedAt)",
        "population": "Contracts whose tipo_de_contrato is exactly 'Obra' and fecha_de_firma is from 2020-01-01 inclusive to 2026-01-01 exclusive",
        "grain": "One record per contract in SECOP II; source endpoint aggregated server-side to signature-year totals",
        "source_fields_used": ["tipo_de_contrato", "fecha_de_firma", "dias_adicionados"],
        "excluded_source_fields": "Supplier names/documents/IDs, legal-representative details, bank/account data, contract addresses and free-text objects were not selected or downloaded.",
        "queries": {"all_contracts": all_query, "positive_extension_days": extended_query},
        "snapshot_files": {key: {"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)} for key, path in files.items()},
        "contracts_in_period": all_contracts,
        "contracts_with_positive_extension_days": ext_contracts,
        "period_share_with_positive_extension_days": ext_contracts / all_contracts,
        "annual_rows": rows,
        "interpretation": "Administrative snapshot indicator of reported contract-term extensions; not delay, non-performance, default, fraud, vendor quality, payment risk, or causal evidence.",
        "limits": ["Cohorts have unequal exposure time: later signed contracts have had less time to be amended.",
                   "The dataset is updated after signature and may reflect current contract state; amendment history is not reconstructed here.",
                   "A reported extension can have legitimate causes and is not an adverse outcome by itself.",
                   "No contractor identity or contract-level panel was downloaded; vendor concentration/performance cannot be assessed.",
                   "The open dataset's license field is blank; this companion stores aggregate API responses and records source attribution, not a claim about legal reuse of all fields."]
    }
    (OUT / "source_and_qa.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    ax.bar([str(row["signature_year"]) for row in rows], [row["works_contracts"] for row in rows], color="#567c8d", alpha=.85)
    ax.set_ylabel("Contratos de obra registrados")
    ax.set_xlabel("Año de firma")
    ax.set_title("SECOP II: contratos de obra y extensiones contractuales reportadas")
    ax.grid(axis="y", alpha=.22)
    ax2 = ax.twinx()
    ax2.plot([str(row["signature_year"]) for row in rows], [100*row["share_with_positive_extension_days"] for row in rows], color="#c2513a", marker="o", lw=2)
    ax2.set_ylabel("Con días adicionados positivos (%)", color="#9a3b2d")
    ax2.set_ylim(bottom=0)
    fig.text(.01, .005, "Cohortes con seguimiento desigual; extensión no equivale a retraso ni incumplimiento.", fontsize=9)
    fig.tight_layout(rect=(0, .03, 1, 1))
    fig.savefig(OUT / "works_extension_proxy.png", dpi=170, facecolor="white")
    plt.close(fig)
    print(json.dumps({"contracts": all_contracts, "contracts_with_extension_days": ext_contracts,
                      "period_share": round(ext_contracts / all_contracts, 4),
                      "annual": rows, "snapshot_hashes": metadata["snapshot_files"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
