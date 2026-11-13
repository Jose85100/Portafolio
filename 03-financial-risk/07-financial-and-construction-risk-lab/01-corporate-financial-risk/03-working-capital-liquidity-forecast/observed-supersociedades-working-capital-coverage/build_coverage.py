#!/usr/bin/env python3
"""Aggregate availability of official working-capital inputs; never builds CCC."""
from __future__ import annotations

import csv
import hashlib
import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import date
from io import BytesIO
from pathlib import Path

import certifi
import matplotlib.pyplot as plt
import openpyxl

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data"
COHORT_URL = "https://www.supersociedades.gov.co/documents/80312/9178350/Base_1000_empresas_2024.xlsx"
SOURCES = {
    "bs_2023": {"id": "pfdp-zks5", "year": 2023, "taxonomy": 369, "concepts": {
        "receivables": "Cuentas comerciales por cobrar y otras cuentas por cobrar corrientes",
        "inventories": "Inventarios corrientes", "payables": "Cuentas por pagar comerciales y otras cuentas por pagar corrientes"}},
    "bs_2024": {"id": "pfdp-zks5", "year": 2024, "taxonomy": 411, "concepts": {
        "receivables": "Cuentas comerciales por cobrar y otras cuentas por cobrar corrientes",
        "inventories": "Inventarios corrientes", "payables": "Cuentas por pagar comerciales y otras cuentas por pagar corrientes"}},
    "is_2024": {"id": "prwj-nzxa", "year": 2024, "taxonomy": 411, "concepts": {
        "revenue": "Ingresos de actividades ordinarias", "cost_of_sales": "Costo de ventas"}},
}
CHUNK_SIZE, PAGE_SIZE, TIMEOUT, RETRIES = 80, 5000, 45, 3
DETAILED_BASES = {
    "10 niif plenas - individual grupo 1", "20 niif plenas - separado grupo 1",
    "30 niif plenas - consolidado grupo 1", "35 niif plenas - combinado grupo 1",
    "40 niif pymes - individual grupo 2", "50 niif pymes - separado grupo 2",
}


def get_bytes(url: str, context: ssl.SSLContext) -> bytes:
    last_error = None
    for attempt in range(RETRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "portfolio-working-capital-coverage/1.0"})
            with urllib.request.urlopen(req, context=context, timeout=TIMEOUT) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt + 1 < RETRIES:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Official endpoint failed after {RETRIES} attempts: {last_error}")


def load_cohort(workbook_bytes: bytes):
    ws = openpyxl.load_workbook(BytesIO(workbook_bytes), data_only=True, read_only=True).active
    cohort = []
    for row in ws.iter_rows(min_row=6, values_only=True):
        if len(row) < 20 or row[1] is None or not row[8]:
            continue
        try:
            nit = str(int(float(row[1])))
        except (TypeError, ValueError, OverflowError):
            continue
        cohort.append({"nit": nit, "sector": str(row[8]).strip(), "basis": str(row[19]).strip()})
    if len(cohort) != len({x["nit"] for x in cohort}):
        raise ValueError("Duplicate NITs in official top-1,000 cohort workbook.")
    if len(cohort) != 1000:
        raise ValueError(f"Expected 1,000 cohort rows, found {len(cohort)}.")
    return cohort, hashlib.sha256(workbook_bytes).hexdigest()


def retrieve(source_key: str, cohort: list[dict], context: ssl.SSLContext):
    source = SOURCES[source_key]
    concept_names = list(source["concepts"].values())
    reports = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(set))))
    value_counts = Counter()
    response_hash, response_bytes, raw_rows = hashlib.sha256(), 0, 0
    for start in range(0, len(cohort), CHUNK_SIZE):
        chunk = cohort[start:start + CHUNK_SIZE]
        nits = [r["nit"] for r in chunk]
        where = (
            f'fecha_corte="{source["year"]}-12-31T00:00:00" and periodo="Periodo Actual" '
            f'and id_taxonomia={source["taxonomy"]} and concepto in ({",".join(json.dumps(c, ensure_ascii=False) for c in concept_names)}) '
            f'and nit in ({",".join(nits)})'
        )
        offset = 0
        while True:
            params = {
                "$select": "nit,codigo_instancia,punto_entrada,concepto,valor",
                "$where": where, "$limit": str(PAGE_SIZE), "$offset": str(offset),
            }
            payload = get_bytes(f'https://www.datos.gov.co/resource/{source["id"]}.json?' + urllib.parse.urlencode(params), context)
            response_hash.update(payload)
            response_bytes += len(payload)
            page = json.loads(payload)
            raw_rows += len(page)
            for row in page:
                try:
                    nit, filing = str(int(row["nit"])), str(int(row["codigo_instancia"]))
                    basis, concept = str(row["punto_entrada"]).strip(), row["concepto"]
                    value = float(str(row["valor"]).replace(",", "."))
                except (KeyError, TypeError, ValueError, OverflowError):
                    continue
                if concept in concept_names and basis:
                    reports[nit][filing][basis][concept].add(value)
                    value_counts[(nit, filing, basis, concept, repr(value))] += 1
            if len(page) < PAGE_SIZE:
                break
            offset += len(page)
        time.sleep(0.12)

    aligned, ambiguous, conflict_keys = {}, 0, 0
    basis_counts = Counter()
    for entity in cohort:
        nit, declared = entity["nit"], entity["basis"].casefold()
        candidate_bases = {basis for filings in reports.get(nit, {}).values() for basis in filings}
        if declared in DETAILED_BASES:
            chosen_bases = {basis for basis in candidate_bases if basis.casefold() == declared}
        elif declared in {"grupo 1", "grupo 2"}:
            chosen_bases = {basis for basis in candidate_bases if declared in basis.casefold()}
            if len(chosen_bases) > 1:
                ambiguous += 1
                continue
        else:
            chosen_bases = set()
        if not chosen_bases:
            continue
        basis = next(iter(chosen_bases))
        eligible_filings = []
        for filing, bases in reports.get(nit, {}).items():
            if basis not in bases:
                continue
            eligible_filings.append((int(filing), bases[basis]))
        if not eligible_filings:
            continue
        _, values = max(eligible_filings, key=lambda item: item[0])
        clean = {}
        conflicted = False
        for concept, numeric_values in values.items():
            if len(numeric_values) != 1:
                conflict_keys += 1
                conflicted = True
                continue
            clean[concept] = next(iter(numeric_values))
        if conflicted:
            continue
        aligned[nit] = clean
        basis_counts[basis] += 1
    qa = {
        "dataset_id": source["id"], "financial_year": source["year"], "taxonomy_id": source["taxonomy"],
        "concepts_requested": source["concepts"], "source_rows_returned": raw_rows,
        "entities_with_aligned_basis_and_report": len(aligned), "entities_without_aligned_basis_or_report": len(cohort) - len(aligned),
        "ambiguous_generic_basis_exclusions": ambiguous, "conflicting_filing_concept_keys": conflict_keys,
        "exact_duplicate_rows_collapsed": sum(n - 1 for n in value_counts.values() if n > 1),
        "selected_basis_counts": dict(sorted(basis_counts.items())),
        "response_sha256": response_hash.hexdigest(), "response_bytes": response_bytes,
    }
    return aligned, qa


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    context = ssl.create_default_context(cafile=certifi.where())
    workbook = get_bytes(COHORT_URL, context)
    cohort, cohort_sha = load_cohort(workbook)
    observations, quality = {}, {}
    for key in SOURCES:
        observations[key], quality[key] = retrieve(key, cohort, context)
    counts_by_sector = defaultdict(lambda: Counter())
    dio_by_sector = defaultdict(list)
    sector_population = Counter(row["sector"] for row in cohort)
    for row in cohort:
        nit, sector = row["nit"], row["sector"]
        present = {k: nit in observations[k] for k in SOURCES}
        for key, concept_map in (("bs_2023", SOURCES["bs_2023"]["concepts"]), ("bs_2024", SOURCES["bs_2024"]["concepts"]), ("is_2024", SOURCES["is_2024"]["concepts"])):
            for metric, concept in concept_map.items():
                if present[key] and concept in observations[key][nit]:
                    counts_by_sector[sector][f"{metric}_{key}_present"] += 1
        bs23, bs24, is24 = (observations[k].get(nit, {}) for k in ("bs_2023", "bs_2024", "is_2024"))
        if all(SOURCES["bs_2023"]["concepts"][m] in bs23 for m in ("receivables", "inventories", "payables")):
            counts_by_sector[sector]["all_three_balance_concepts_2023_present"] += 1
        if all(SOURCES["bs_2024"]["concepts"][m] in bs24 for m in ("receivables", "inventories", "payables")):
            counts_by_sector[sector]["all_three_balance_concepts_2024_present"] += 1
        if all(SOURCES["is_2024"]["concepts"][m] in is24 for m in ("revenue", "cost_of_sales")):
            counts_by_sector[sector]["revenue_and_cost_of_sales_2024_present"] += 1
        if (
            all(SOURCES["bs_2023"]["concepts"][m] in bs23 for m in ("receivables", "inventories", "payables"))
            and all(SOURCES["bs_2024"]["concepts"][m] in bs24 for m in ("receivables", "inventories", "payables"))
            and all(SOURCES["is_2024"]["concepts"][m] in is24 for m in ("revenue", "cost_of_sales"))
        ):
            counts_by_sector[sector]["all_selected_source_fields_present"] += 1
        inv23 = bs23.get(SOURCES["bs_2023"]["concepts"]["inventories"])
        inv24 = bs24.get(SOURCES["bs_2024"]["concepts"]["inventories"])
        cogs24 = is24.get(SOURCES["is_2024"]["concepts"]["cost_of_sales"])
        if inv23 is not None and inv24 is not None and cogs24 is not None and (inv23 + inv24) > 0 and cogs24 > 0:
            dio_by_sector[sector].append(((inv23 + inv24) / 2) / cogs24 * 365)

    metric_keys = [
        "receivables_bs_2023_present", "inventories_bs_2023_present", "payables_bs_2023_present",
        "receivables_bs_2024_present", "inventories_bs_2024_present", "payables_bs_2024_present",
        "revenue_is_2024_present", "cost_of_sales_is_2024_present",
        "all_three_balance_concepts_2023_present", "all_three_balance_concepts_2024_present",
        "revenue_and_cost_of_sales_2024_present", "all_selected_source_fields_present",
    ]
    output_rows = []
    for sector, population in sorted(sector_population.items()):
        row = {"macro_sector": sector, "cohort_top1000_entities": population}
        for key in metric_keys:
            count = counts_by_sector[sector][key]
            row[key] = count
            row[key.replace("_present", "_coverage_pct")] = round(100 * count / population, 1)
        dio_values = sorted(dio_by_sector[sector])
        n_dio = len(dio_values)
        row["eligible_inventory_days_dio_entities"] = n_dio
        row["inventory_days_dio_coverage_pct"] = round(100 * n_dio / population, 1)
        row["median_inventory_days_dio"] = None if not n_dio else round(dio_values[n_dio // 2] if n_dio % 2 else (dio_values[n_dio // 2 - 1] + dio_values[n_dio // 2]) / 2, 2)
        output_rows.append(row)
    csv_path = OUT / "input_coverage_by_sector.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)

    fig, ax = plt.subplots(figsize=(10, 6))
    matrix = [[row[key.replace("_present", "_coverage_pct")] for key in metric_keys[:8]] for row in output_rows]
    im = ax.imshow(matrix, aspect="auto", cmap="Blues", vmin=0, vmax=100)
    labels = [k.replace("_present", "").replace("_bs_", " ").replace("_is_", " ").replace("_", " ").title() for k in metric_keys[:8]]
    ax.set_xticks(range(len(labels)), labels, rotation=42, ha="right")
    ax.set_yticks(range(len(output_rows)), [r["macro_sector"].replace("-", " ").title() for r in output_rows])
    ax.set_title("Official NIIF input coverage in the matched top-1,000 cohort")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Coverage of each macro-sector cohort (%)")
    fig.tight_layout()
    figure = OUT / "input_coverage_heatmap.png"
    fig.savefig(figure, dpi=180)
    plt.close(fig)
    dio_rows = [r for r in output_rows if r["median_inventory_days_dio"] is not None]
    dio_rows.sort(key=lambda r: r["median_inventory_days_dio"])
    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.barh([r["macro_sector"].replace("-", " ").title() for r in dio_rows], [r["median_inventory_days_dio"] for r in dio_rows], color="#176b87")
    ax.set(title="Inventory days (DIO) from aligned 2023–2024 filings", xlabel="Average current inventory / 2024 cost of sales × 365 days")
    ax.grid(axis="x", alpha=.22)
    ax.set_axisbelow(True)
    for bar, row in zip(bars, dio_rows):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f"  n={row['eligible_inventory_days_dio_entities']}", va="center", fontsize=8)
    fig.tight_layout()
    dio_figure = OUT / "median_inventory_days_dio.png"
    fig.savefig(dio_figure, dpi=180)
    plt.close(fig)
    manifest = {
        "cohort_source": COHORT_URL, "cohort_vintage": "Supersociedades 2025 report, 2024 financial cut",
        "cohort_rows": len(cohort), "cohort_sha256": cohort_sha, "snapshot_date": date.today().isoformat(),
        "data_sources": {
            "balance_sheet": "https://www.datos.gov.co/Economy-and-Finances/Estados-Financieros-NIIF-Estado-de-Situaci-n-Finan/pfdp-zks5",
            "income_statement": "https://www.datos.gov.co/resource/prwj-nzxa.json",
            "unit_guidance": "https://www.supersociedades.gov.co/web/asuntos-economicos-societarios/preguntas-frecuentes",
        },
        "join_and_selection": "NIT and report basis are processed in memory only. Exact cohort basis is required; generic group labels with multiple report bases are excluded. Latest codigo_instancia within the aligned basis is retained for each dataset/year. No entity-level rows or identifiers are persisted.",
        "units": "All three NIIF account fields are reported in thousands of COP per official FAQ; only coverage counts and unit-free DIO days are released.",
        "derived_metric": "Median inventory-days (DIO) = ((2023-12-31 current inventory + 2024-12-31 current inventory)/2) / 2024 cost of sales * 365. Included only when all three same-basis observations are present and average inventory and cost of sales are positive. No DSO, DPO, CCC, forecast, or LaR is derived.",
        "quality_by_source": quality,
        "output_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        "figure_sha256": hashlib.sha256(figure.read_bytes()).hexdigest(),
        "dio_figure_sha256": hashlib.sha256(dio_figure.read_bytes()).hexdigest(),
        "outputs_contain_entity_or_filing_identifiers": False,
        "semantic_gaps": [
            "Revenue is total ordinary operating revenue, not credit sales; therefore exact DSO cannot be derived.",
            "Cost of sales is not supplier purchases; payables days/DPO cannot be derived without assumptions that are not validated here.",
            "Receivables and payables concepts include other accounts, so they are broader than pure trade balances.",
            "The DIO component is a stock-to-flow accounting measure, not an observed inventory depletion/turnover series or a cash-cycle measure.",
            "No observed cash collection/payment dates, forecast vintages, committed liquidity, or shortfall outcomes are present; no CCC, cash forecast, or LaR is estimated."
        ]
    }
    (OUT / "source_quality_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build()
