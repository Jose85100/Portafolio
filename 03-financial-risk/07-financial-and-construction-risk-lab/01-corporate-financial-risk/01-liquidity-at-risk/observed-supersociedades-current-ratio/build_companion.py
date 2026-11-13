#!/usr/bin/env python3
"""Build sector aggregates by joining official Supersociedades sources in memory."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date
from io import BytesIO
from pathlib import Path

import certifi
import matplotlib.pyplot as plt
import openpyxl

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data"
EXCEL_URL = "https://www.supersociedades.gov.co/documents/80312/9178350/Base_1000_empresas_2024.xlsx"
API = "https://www.datos.gov.co/resource/pfdp-zks5.json"
DATASET_ID = "pfdp-zks5"
CONCEPTS = ("Activos corrientes totales", "Pasivos corrientes totales")
YEAR = 2024
CHUNK_SIZE = 40
TIMEOUT_SECONDS = 45
RETRIES = 3


def http_get(url: str, context: ssl.SSLContext) -> bytes:
    last_error = None
    for attempt in range(RETRIES):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "portfolio-liquidity-context/1.0"})
            with urllib.request.urlopen(request, context=context, timeout=TIMEOUT_SECONDS) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt + 1 < RETRIES:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Official endpoint did not respond after {RETRIES} attempts: {last_error}")


def parse_company_cohort(workbook_bytes: bytes) -> tuple[list[dict], str]:
    wb = openpyxl.load_workbook(BytesIO(workbook_bytes), data_only=True, read_only=True)
    ws = wb.active
    items = []
    for row in ws.iter_rows(min_row=6, values_only=True):
        nit_value = row[1] if len(row) > 1 else None
        sector = row[8] if len(row) > 8 else None
        basis = row[19] if len(row) > 19 else None
        if nit_value is None or not sector:
            continue
        try:
            nit = str(int(float(nit_value)))
        except (TypeError, ValueError, OverflowError):
            continue
        items.append({"nit": nit, "sector": str(sector).strip(), "basis": str(basis).strip() if basis is not None else ""})
    wb.close()
    if not items:
        raise ValueError("The official top-1,000 workbook did not contain NIT/macro-sector rows at the expected schema.")
    if len(items) != len({x["nit"] for x in items}):
        raise ValueError("Duplicate NITs found in the official cohort workbook; resolve before joining.")
    return items, hashlib.sha256(workbook_bytes).hexdigest()


def fetch_accounts(cohort: list[dict], context: ssl.SSLContext) -> tuple[list[dict], dict]:
    by_nit: dict[str, dict[str, dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
    value_occurrences: dict[tuple[str, str, str, str], int] = defaultdict(int)
    filing_basis: dict[str, dict[str, str]] = defaultdict(dict)
    response_hash = hashlib.sha256()
    response_bytes = 0
    raw_rows = 0
    queried_nits = set()
    for start in range(0, len(cohort), CHUNK_SIZE):
        nits = [item["nit"] for item in cohort[start:start + CHUNK_SIZE]]
        queried_nits.update(nits)
        where = (
            f'fecha_corte="{YEAR}-12-31T00:00:00" and periodo="Periodo Actual" '
            f'and id_taxonomia=411 and concepto in ("{CONCEPTS[0]}","{CONCEPTS[1]}") '
            f'and nit in ({",".join(nits)})'
        )
        offset = 0
        while True:
            params = {
                "$select": "nit,codigo_instancia,punto_entrada,concepto,valor",
                "$where": where,
                "$limit": "5000",
                "$offset": str(offset),
            }
            payload = http_get(API + "?" + urllib.parse.urlencode(params), context)
            response_hash.update(payload)
            response_bytes += len(payload)
            page = json.loads(payload)
            raw_rows += len(page)
            for record in page:
                try:
                    nit = str(int(record["nit"]))
                    filing = str(int(record["codigo_instancia"]))
                    concept = record["concepto"]
                    value = float(str(record["valor"]).replace(",", "."))
                    basis = str(record.get("punto_entrada", "")).strip()
                except (KeyError, TypeError, ValueError, OverflowError):
                    continue
                if concept in CONCEPTS and math.isfinite(value):
                    by_nit[nit][filing].setdefault(concept, {})
                    by_nit[nit][filing][concept][repr(value)] = value
                    value_occurrences[(nit, filing, concept, repr(value))] += 1
                    if basis:
                        filing_basis[nit][filing] = basis
            if len(page) < 5000:
                break
            offset += len(page)
        time.sleep(0.15)

    cohort_nits = {x["nit"] for x in cohort}
    records, duplicate_exact, conflicting, ambiguous_basis = [], 0, 0, 0
    explicit_basis_matches, generic_group_matches = 0, 0
    cohort_by_nit = {x["nit"]: x for x in cohort}
    detailed_labels = {
        "10 niif plenas - individual grupo 1", "20 niif plenas - separado grupo 1",
        "30 niif plenas - consolidado grupo 1", "40 niif pymes - individual grupo 2",
        "50 niif pymes - separado grupo 2",
    }
    for nit in cohort_nits:
        filings = by_nit.get(nit, {})
        complete = []
        for filing, concepts in filings.items():
            values = {}
            for concept in CONCEPTS:
                vals = concepts.get(concept, {})
                if len(vals) > 1:
                    conflicting += 1
                elif len(vals) == 1:
                    values[concept] = next(iter(vals.values()))
            if len(values) == 2:
                complete.append((int(filing), values, filing_basis.get(nit, {}).get(filing, "")))
        if not complete:
            continue
        expected = cohort_by_nit[nit]["basis"].casefold()
        if expected in detailed_labels:
            candidates = [r for r in complete if r[2].casefold() == expected]
            explicit_basis_matches += bool(candidates)
        elif expected in {"grupo 1", "grupo 2"}:
            group = expected
            candidates = [r for r in complete if group in r[2].casefold()]
            if len({r[2] for r in candidates}) > 1:
                ambiguous_basis += 1
                continue
            generic_group_matches += bool(candidates)
        else:
            continue
        if not candidates:
            continue
        # Retain the greatest complete instance ID within the declared basis.
        filing, values, _ = max(candidates, key=lambda pair: pair[0])
        records.append({"nit": nit, "filing": filing, "assets": values[CONCEPTS[0]], "liabilities": values[CONCEPTS[1]]})
    duplicate_exact = sum(max(0, n - 1) for n in value_occurrences.values())
    qa = {
        "cohort_entities": len(cohort), "nits_queried": len(queried_nits), "source_rows_returned": raw_rows,
        "matched_entities_with_both_accounts_and_aligned_basis": len(records),
        "entities_without_both_accounts_or_aligned_basis": len(cohort) - len(records),
        "explicit_basis_matches": explicit_basis_matches,
        "generic_group_basis_matches": generic_group_matches,
        "ambiguous_generic_group_basis_exclusions": ambiguous_basis,
        "exact_duplicate_rows_collapsed_or_repeated_values": duplicate_exact,
        "conflicting_values_within_filing_concept": conflicting,
        "api_response_sha256": response_hash.hexdigest(), "api_response_bytes": response_bytes,
    }
    if conflicting:
        raise ValueError(f"Found {conflicting} filing/concept keys with conflicting values; refusing to aggregate.")
    return records, qa


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    context = ssl.create_default_context(cafile=certifi.where())
    workbook_bytes = http_get(EXCEL_URL, context)
    cohort, workbook_sha = parse_company_cohort(workbook_bytes)
    records, qa = fetch_accounts(cohort, context)
    sector_by_nit = {row["nit"]: row["sector"] for row in cohort}
    stats = defaultdict(lambda: {"ratios": [], "assets": 0.0, "liabilities": 0.0, "n": 0})
    for record in records:
        if record["assets"] <= 0 or record["liabilities"] <= 0:
            continue
        sector = sector_by_nit[record["nit"]]
        current = stats[sector]
        current["ratios"].append(record["assets"] / record["liabilities"])
        current["assets"] += record["assets"]
        current["liabilities"] += record["liabilities"]
        current["n"] += 1
    sector_cohort = defaultdict(int)
    for row in cohort:
        sector_cohort[row["sector"]] += 1
    summaries = []
    for sector in sorted(sector_cohort):
        s = stats[sector]
        ratios = sorted(s["ratios"])
        n = len(ratios)
        median = None if not n else (ratios[n // 2] if n % 2 else (ratios[n // 2 - 1] + ratios[n // 2]) / 2)
        summaries.append({
            "macro_sector": sector,
            "cohort_top1000_entities": sector_cohort[sector],
            "matched_positive_current_accounts": n,
            "coverage_pct_of_sector_cohort": round(n / sector_cohort[sector] * 100, 1),
            "median_entity_current_ratio": None if median is None else round(median, 4),
            "aggregate_current_ratio_ratio_of_sums": None if not s["liabilities"] else round(s["assets"] / s["liabilities"], 4),
        })
    output = OUT / "sector_current_liquidity.csv"
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)
    plot_rows = [r for r in summaries if r["median_entity_current_ratio"] is not None]
    plot_rows.sort(key=lambda r: r["median_entity_current_ratio"])
    fig, ax = plt.subplots(figsize=(10, 6))
    labels = [r["macro_sector"].replace("-", " ").title() for r in plot_rows]
    values = [r["median_entity_current_ratio"] for r in plot_rows]
    bars = ax.barh(labels, values, color="#176b87")
    ax.axvline(1, color="#b4483f", linestyle="--", linewidth=1.3, label="Current assets = current liabilities")
    ax.set(title="Supersociedades top-1,000 cohort: median current ratio", xlabel="Current assets / current liabilities (per matched entity)")
    ax.grid(axis="x", alpha=.22)
    ax.set_axisbelow(True)
    ax.legend(frameon=False)
    for bar, row in zip(bars, plot_rows):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f"  n={row['matched_positive_current_accounts']}", va="center", fontsize=8)
    fig.tight_layout()
    figure = OUT / "sector_median_current_ratio.png"
    fig.savefig(figure, dpi=180)
    plt.close(fig)
    manifest = {
        "provider": "Superintendencia de Sociedades; official source file hosted at supersociedades.gov.co",
        "cohort_source": EXCEL_URL,
        "account_data_source": "Superintendencia de Sociedades NIIF financial statements via Datos Abiertos Colombia",
        "account_dataset_id": DATASET_ID,
        "account_dataset_page": "https://www.datos.gov.co/Economy-and-Finances/Estados-Financieros-NIIF-Estado-de-Situaci-n-Finan/pfdp-zks5",
        "snapshot_date": date.today().isoformat(), "financial_cut": f"{YEAR}-12-31", "cohort_vintage": "2025 report, 2024 financial cut",
        "cohort_size": len(cohort), "cohort_workbook_sha256": workbook_sha,
        "account_concepts": list(CONCEPTS), "api_filters": "fecha_corte=2024-12-31; periodo=Periodo Actual; id_taxonomia=411; matched NITs from official 1,000-company workbook",
        "data_processing": "Join NIT in memory only. Require point_entrada to align with the cohort workbook basis; exclude ambiguous generic group matches. Collapse exact filing/concept/value duplicates. If multiple aligned filings remain, retain the greatest codigo_instancia. No entity-level input/output is written to repository.",
        "qa": qa,
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "figure_sha256": hashlib.sha256(figure.read_bytes()).hexdigest(),
        "outputs_contain_entity_identifiers": False,
        "units": "Supersociedades guidance requires NIIF reports in thousands of COP; ratios are unit-free. Absolute amounts are not released.",
        "limitations": [
            "Top 1,000 entities are selected by operating revenue, not a representative sample of all Colombian companies.",
            "Only entities matched across the two official sources and with both positive current-account values enter the ratio statistics; coverage is disclosed by macro-sector.",
            "The cross-source match and selection of latest basis-aligned filing instance are analytical rules, not institutionally approved linkage or entity-level validation.",
            "Current ratio is a static balance-sheet measure and does not capture timing, cash-flow volatility, liquidity buffers, committed facilities, or shortfalls.",
            "Sector medians and ratio-of-sums are descriptive context, not liquidity-at-risk, a forecast, a PD, a solvency opinion, or individual-company performance.",
            "Supersociedades cohort data are 2024 year-end from the 2025 report."
        ]
    }
    manifest["unit_guidance_source"] = "https://www.supersociedades.gov.co/web/asuntos-economicos-societarios/preguntas-frecuentes"
    (OUT / "source_quality_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build()
