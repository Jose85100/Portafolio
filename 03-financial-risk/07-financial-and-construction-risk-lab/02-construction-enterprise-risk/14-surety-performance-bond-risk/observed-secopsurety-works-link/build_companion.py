#!/usr/bin/env python3
"""Link public SECOP II guarantee rows to contracts classified as works.

Only minimal linkage fields are requested. Contract IDs and all source rows are
kept in memory; repository outputs contain aggregate counts and source hashes.
"""
from __future__ import annotations

import csv
import hashlib
import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import certifi
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
CONTRACTS_API = "https://www.datos.gov.co/resource/jbjy-vk9h.json"
GUARANTEES_API = "https://www.datos.gov.co/resource/gjp9-cutm.json"
PAGE_SIZE = 5000
MAX_RETRIES = 5
CTX = ssl.create_default_context(cafile=certifi.where())


def get_json(url: str) -> tuple[bytes, dict]:
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Portafolio-SECOP-Surety-Companion/1.0"})
            with urllib.request.urlopen(req, context=CTX, timeout=60) as res:
                payload = res.read()
                return payload, {"status": res.status, "etag": res.headers.get("ETag"), "last_modified": res.headers.get("Last-Modified")}
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt + 1 == MAX_RETRIES:
                break
            time.sleep(min(2 ** attempt, 16))
    raise RuntimeError(f"API request failed after {MAX_RETRIES} attempts: {last_error}")


def query_url(base: str, params: dict[str, str]) -> str:
    return base + "?" + urllib.parse.urlencode(params)


def fetch_rows(base: str, select: str, where: str | None, order: str | None = None) -> tuple[list[dict], dict]:
    count_params = {"$select": "count(*) as n"}
    if where:
        count_params["$where"] = where
    count_payload, count_headers = get_json(query_url(base, count_params))
    expected_rows = int(json.loads(count_payload)[0]["n"])
    rows: list[dict] = []
    page_manifest = []
    offset = 0
    while offset < expected_rows:
        params = {"$select": select, "$limit": str(PAGE_SIZE), "$offset": str(offset)}
        if where:
            params["$where"] = where
        if order:
            params["$order"] = order
        payload, headers = get_json(query_url(base, params))
        page = json.loads(payload)
        page_manifest.append({"offset": offset, "rows": len(page), "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(), **headers})
        rows.extend(page)
        if not page:
            break
        offset += len(page)
    if len(rows) != expected_rows:
        raise ValueError(f"Source row-count mismatch: expected {expected_rows}, received {len(rows)}")
    source_manifest = {
        "api": base, "where": where, "selected_fields": select.split(","),
        "rows_reported_by_count_query": expected_rows, "rows_received": len(rows),
        "count_query_sha256": hashlib.sha256(count_payload).hexdigest(),
        "count_query_headers": count_headers, "pages": page_manifest,
        "combined_page_bytes_sha256": hashlib.sha256("".join(p["sha256"] for p in page_manifest).encode()).hexdigest(),
    }
    return rows, source_manifest


def main() -> None:
    built_at = datetime.now(timezone.utc).isoformat()
    contracts, contracts_manifest = fetch_rows(CONTRACTS_API, "id_contrato", "tipo_de_contrato='Obra'")
    obra_ids = {row.get("id_contrato", "").strip() for row in contracts if row.get("id_contrato")}
    null_contract_ids = sum(not row.get("id_contrato") for row in contracts)
    if not obra_ids:
        raise ValueError("No work contract IDs returned")

    guarantees, guarantees_manifest = fetch_rows(
        GUARANTEES_API, "id_contrato,tipopoliza,subtipopoliza,estado", None
    )
    status_subtype = Counter()
    matched_rows = 0
    unmatched_null_id_rows = 0
    ids_with_guarantee = set()
    ids_with_accepted_row = set()
    for row in guarantees:
        contract_id = (row.get("id_contrato") or "").strip()
        if not contract_id:
            unmatched_null_id_rows += 1
            continue
        if contract_id not in obra_ids:
            continue
        matched_rows += 1
        ids_with_guarantee.add(contract_id)
        status = (row.get("estado") or "(vacío)").strip()
        subtype = (row.get("subtipopoliza") or "(vacío)").strip()
        status_subtype[(status, subtype)] += 1
        if status.casefold() == "aceptada":
            ids_with_accepted_row.add(contract_id)

    coverage_by_status = [
        {"status": status, "guarantee_subtype": subtype, "matched_source_rows": count}
        for (status, subtype), count in sorted(status_subtype.items(), key=lambda x: (-x[1], x[0][0], x[0][1]))
    ]
    matched_works = len(ids_with_guarantee)
    accepted_works = len(ids_with_accepted_row)
    summary = {
        "purpose": "Administrative linkage coverage only; not proof of enforceable guarantee, claim, payout, recovery, or loss.",
        "observation_utc": built_at,
        "work_contract_rows": len(contracts), "unique_work_contract_ids": len(obra_ids),
        "work_contract_rows_missing_id": null_contract_ids,
        "guarantee_source_rows": len(guarantees),
        "guarantee_rows_with_missing_contract_id": unmatched_null_id_rows,
        "guarantee_rows_linked_to_work_contracts": matched_rows,
        "unique_work_contracts_with_any_guarantee_row": matched_works,
        "share_work_contract_ids_with_any_guarantee_row_pct": round(100 * matched_works / len(obra_ids), 4),
        "unique_work_contracts_with_at_least_one_accepted_status_row": accepted_works,
        "share_work_contract_ids_with_at_least_one_accepted_status_row_pct": round(100 * accepted_works / len(obra_ids), 4),
        "linked_rows_by_status_and_subtype": coverage_by_status,
        "source_manifest": {"contracts": contracts_manifest, "guarantees": guarantees_manifest},
        "limitations": [
            "The guarantee endpoint includes multiple instrument subtypes; not every row is a performance bond or works guarantee.",
            "There is no stable policy/version key in the selected fields; source rows can include revisions or multiple guarantees per contract.",
            "An accepted administrative status does not establish legal sufficiency, current validity, covered obligation, claim, payout, or recovery.",
            "No work-level contract outcomes, construction completion, contractor default, claim, paid loss, or recovery data are included.",
            "The endpoints are mutable; row counts and match rates describe this extraction vintage only.",
            "IDs are processed in memory and never written to repository outputs; no policy numbers, personal names, beneficiaries, or insurer names are requested.",
        ],
    }
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    with (out / "linked_rows_by_status_subtype.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["status", "guarantee_subtype", "matched_source_rows"])
        writer.writeheader(); writer.writerows(coverage_by_status)
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    fig, ax = plt.subplots(figsize=(9, 5))
    status_counts = Counter()
    for row in coverage_by_status:
        status_counts[row["status"]] += row["matched_source_rows"]
    labels = [k for k, _ in status_counts.most_common()]
    values = [status_counts[k] for k in labels]
    ax.barh(labels[::-1], values[::-1], color="#347c91")
    ax.set_xlabel("Filas de garantía enlazadas (puede incluir revisiones/múltiples amparos)")
    ax.set_title("Registros de garantía SECOP II enlazados a contratos clasificados como Obra")
    ax.grid(axis="x", alpha=.22)
    fig.tight_layout()
    fig_path = out / "linked_guarantee_rows_by_status.png"
    fig.savefig(fig_path, dpi=170); plt.close(fig)
    manifest = {
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "summary_sha256": hashlib.sha256((out / "summary.json").read_bytes()).hexdigest(),
        "status_csv_sha256": hashlib.sha256((out / "linked_rows_by_status_subtype.csv").read_bytes()).hexdigest(),
        "figure_sha256": hashlib.sha256(fig_path.read_bytes()).hexdigest(),
        "extract_utc": built_at,
        "source_ids": {"contracts": "jbjy-vk9h", "guarantees": "gjp9-cutm"},
        "raw_source_rows_retained": False,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "source_manifest"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
