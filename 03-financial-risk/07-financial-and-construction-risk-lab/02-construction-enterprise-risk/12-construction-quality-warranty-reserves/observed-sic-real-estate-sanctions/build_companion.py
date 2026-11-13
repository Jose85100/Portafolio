#!/usr/bin/env python3
"""Summarize final SIC consumer-protection sanctions in the Inmuebles sector."""
from __future__ import annotations

import csv
import hashlib
import json
import ssl
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import certifi
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
API = "https://www.datos.gov.co/resource/73dx-n59j.json"
WHERE = "sector='Inmuebles'"
FIELDS = "res_sancion,fecha_emitida,conducta"


def fetch() -> tuple[list[dict], bytes]:
    params = {"$select": FIELDS, "$where": WHERE, "$limit": "5000"}
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Portfolio-SIC-Property-Sanctions-Companion/1.0"})
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(req, context=context, timeout=45) as response:
        payload = response.read()
        rows = json.loads(payload)
        if response.status != 200:
            raise RuntimeError(f"SIC API returned HTTP {response.status}")
    return rows, payload


def main() -> None:
    observed_at = datetime.now(timezone.utc).isoformat()
    rows, payload = fetch()
    by_resolution: dict[str, list[dict]] = defaultdict(list)
    invalid = 0
    for row in rows:
        resolution = (row.get("res_sancion") or "").strip()
        date = (row.get("fecha_emitida") or "")[:10]
        conduct = (row.get("conducta") or "(vacía)").strip()
        if not resolution or not date:
            invalid += 1
            continue
        by_resolution[resolution].append({"date": date, "conduct": conduct})
    if not by_resolution:
        raise ValueError("No resolutions available in sector filter")
    date_conflicts = sum(len({r["date"] for r in recs}) > 1 for recs in by_resolution.values())
    if date_conflicts:
        raise ValueError(f"Conflicting issue dates for {date_conflicts} resolutions")

    annual_total = Counter()
    annual_quality = Counter()
    conduct_rows = Counter()
    conduct_resolutions: dict[str, set[str]] = defaultdict(set)
    for resolution, records in by_resolution.items():
        year = records[0]["date"][:4]
        annual_total[year] += 1
        quality_resolution = False
        for record in records:
            conduct_rows[record["conduct"]] += 1
            conduct_resolutions[record["conduct"]].add(resolution)
            if "calidad" in record["conduct"].casefold():
                quality_resolution = True
        if quality_resolution:
            annual_quality[year] += 1
    years = sorted(annual_total)
    total_quality = sum(annual_quality.values())
    annual = [{"year": int(y), "unique_final_resolutions": annual_total[y],
               "resolutions_with_quality_labeled_conduct": annual_quality[y]} for y in years]
    by_conduct = [{"conduct": conduct, "source_rows": n,
                   "unique_resolutions": len(conduct_resolutions[conduct])}
                  for conduct, n in sorted(conduct_rows.items(), key=lambda item: (-item[1], item[0]))]

    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    with (out / "annual_unique_resolutions.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(annual[0]))
        writer.writeheader(); writer.writerows(annual)
    with (out / "conduct_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(by_conduct[0]))
        writer.writeheader(); writer.writerows(by_conduct)

    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.bar([str(r["year"]) for r in annual], [r["unique_final_resolutions"] for r in annual], color="#347c91", label="Todas las conductas")
    ax.plot([str(r["year"]) for r in annual], [r["resolutions_with_quality_labeled_conduct"] for r in annual], color="#c76536", marker="o", linewidth=2, label="Con alguna conducta rotulada Calidad")
    ax.set_ylabel("Resoluciones administrativas únicas")
    ax.set_title("SIC: sanciones firmes del sector Inmuebles por año de emisión")
    ax.grid(axis="y", alpha=.22); ax.legend(frameon=False)
    fig.tight_layout()
    fig_path = out / "annual_sanctions.png"
    fig.savefig(fig_path, dpi=170); plt.close(fig)

    summary = {
        "purpose": "Context on final consumer-protection sanctions; not a warranty-claim, defect-rate, reserve, or paid-loss dataset.",
        "observation_utc": observed_at,
        "source_dataset_id": "73dx-n59j",
        "source_url": "https://www.datos.gov.co/Comercio-Industria-y-Turismo/Sanciones-impuestas-en-firme-por-la-SIC/73dx-n59j",
        "filter": WHERE,
        "selected_fields": FIELDS.split(","),
        "source_rows": len(rows),
        "unique_resolution_ids": len(by_resolution),
        "rows_missing_resolution_or_date": invalid,
        "resolution_date_conflicts": date_conflicts,
        "period": [years[0], years[-1]],
        "resolutions_with_quality_labeled_conduct": total_quality,
        "quality_label_is_substring_rule_not_warranty_classification": True,
        "records_by_conduct_allow_multiple_conducts_per_resolution": by_conduct,
        "raw_response_sha256": hashlib.sha256(payload).hexdigest(),
        "limitations": [
            "Sector Inmuebles is not a cohort of construction projects or a denominator of dwellings delivered.",
            "Rows may repeat one resolution across multiple conduct labels; unique resolutions are counted annually, while conduct table is non-exclusive.",
            "A conduct containing Calidad is not necessarily a warranty claim or a defect requiring repair.",
            "The source contains final administrative sanctions, not all complaints, warranty notices, claims, repair costs, payouts, recoveries, or actuarial losses.",
            "The sanction table includes names and case identifiers; only three selected fields are processed and no case IDs or names are written to outputs.",
            "The API is mutable; this extract is a single observed vintage and not a complete census of quality defects.",
        ],
    }
    summary_path = out / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "raw_response_sha256": summary["raw_response_sha256"],
        "summary_sha256": hashlib.sha256(summary_path.read_bytes()).hexdigest(),
        "annual_csv_sha256": hashlib.sha256((out / "annual_unique_resolutions.csv").read_bytes()).hexdigest(),
        "conduct_csv_sha256": hashlib.sha256((out / "conduct_summary.csv").read_bytes()).hexdigest(),
        "figure_sha256": hashlib.sha256(fig_path.read_bytes()).hexdigest(),
        "raw_rows_retained": False,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "records_by_conduct_allow_multiple_conducts_per_resolution"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
