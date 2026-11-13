"""Aggregate concentration profile of public projects in DNP's SGR dataset."""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
RESULTS = BASE / "results"
SOURCE_URL = "https://www.datos.gov.co/resource/mzgh-shtp.json"
METADATA_URL = "https://www.datos.gov.co/api/views/mzgh-shtp.json"
SELECT = "codigobpin,valortotal,sector,departamento,entidadejecutora,estado,ejecucionfisica,ejecucionfinanciera"
PARAMS = {"$select": SELECT, "$order": "codigobpin", "$limit": "50000"}
INCLUDED_STATES = {"TERMINADO", "EN EJECUCIÓN"}
FIELDS = ["codigobpin", "valortotal", "sector", "departamento", "entidadejecutora", "estado", "ejecucionfisica", "ejecucionfinanciera"]
AGG_FIELDS = ["dimension", "category", "project_count", "value_total_reported", "project_share_pct", "value_share_pct"]


def fetch(session: requests.Session, url: str, params=None):
    error = None
    for attempt in range(5):
        try:
            response = session.get(url, params=params, timeout=(15, 120))
            if response.status_code in {429, 500, 502, 503, 504}:
                error = RuntimeError(f"HTTP {response.status_code}: {response.text[:200]}")
                time.sleep(2 ** attempt)
                continue
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            error = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f"No se pudo consultar la fuente DNP tras cinco intentos: {error}")


def number(value):
    if value in (None, ""):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if out == out and abs(out) != float("inf") else None


def refresh_snapshot():
    session = requests.Session()
    session.headers.update({"User-Agent": "Portafolio-Research-Companion/1.0", "Accept-Encoding": "gzip"})
    source_response = fetch(session, SOURCE_URL, PARAMS)
    raw_hash = hashlib.sha256(source_response.content).hexdigest()
    rows = source_response.json()
    metadata = fetch(session, METADATA_URL).json()

    by_bpin = defaultdict(list)
    for row in rows:
        key = str(row.get("codigobpin") or "").strip()
        if key:
            by_bpin[key].append(row)

    project_rows = []
    conflict_counts = defaultdict(int)
    exact_repeated_groups = 0
    extra_duplicate_rows = 0
    for bpin, group in by_bpin.items():
        if len(group) > 1:
            extra_duplicate_rows += len(group) - 1
            if all(tuple(row.get(field) for field in FIELDS[1:]) == tuple(group[0].get(field) for field in FIELDS[1:]) for row in group):
                exact_repeated_groups += 1
        record = {"codigobpin": bpin}
        for field in FIELDS[1:]:
            vals = {str(row.get(field)).strip() for row in group if row.get(field) not in (None, "")}
            if len(vals) > 1:
                conflict_counts[field] += 1
            record[field] = next(iter(vals)) if len(vals) == 1 else None
        # A department is assignable only if all distinct non-empty labels agree.
        dept_vals = {str(row.get("departamento")).strip() for row in group if row.get("departamento") not in (None, "")}
        record["department_unambiguous"] = len(dept_vals) == 1
        record["department"] = next(iter(dept_vals)) if len(dept_vals) == 1 else None
        project_rows.append(record)

    total_project_count = len(project_rows)
    status_counts = defaultdict(int)
    for row in project_rows:
        status_counts[row["estado"] or "SIN ESTADO"] += 1

    included = [row for row in project_rows if row["estado"] in INCLUDED_STATES]
    missing_value = 0
    negative_value = 0
    usable = []
    invalid_execution = 0
    for row in included:
        value = number(row["valortotal"])
        if value is None:
            missing_value += 1
            continue
        if value < 0:
            negative_value += 1
            continue
        row["value"] = value
        for execution_field in ("ejecucionfisica", "ejecucionfinanciera"):
            val = number(row[execution_field])
            if val is not None and not 0 <= val <= 100:
                invalid_execution += 1
        usable.append(row)

    # Department coverage uses only projects with one unambiguous department.
    dept_eligible = [r for r in usable if r["department_unambiguous"]]
    aggregates = defaultdict(lambda: {"project_count": 0, "value_total_reported": 0.0})
    dimension_values = {
        "sector": lambda r: r["sector"],
        "department_unambiguous": lambda r: r["department"] if r["department_unambiguous"] else None,
        "executing_entity": lambda r: r["entidadejecutora"],
    }
    for dim, getter in dimension_values.items():
        subset = dept_eligible if dim == "department_unambiguous" else usable
        total_count = len(subset)
        total_value = sum(r["value"] for r in subset)
        for row in subset:
            category = getter(row)
            if not category:
                category = "SIN DATO"
            cell = aggregates[(dim, category)]
            cell["project_count"] += 1
            cell["value_total_reported"] += row["value"]
        for (d, category), cell in list(aggregates.items()):
            if d == dim:
                cell["project_share_pct"] = cell["project_count"] / total_count * 100 if total_count else 0.0
                cell["value_share_pct"] = cell["value_total_reported"] / total_value * 100 if total_value else 0.0

    DATA.mkdir(exist_ok=True)
    with (DATA / "aggregated_sgr_projects.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=AGG_FIELDS)
        writer.writeheader()
        for (dimension, category), values in sorted(aggregates.items()):
            writer.writerow({"dimension": dimension, "category": category, **values})

    rows_updated = metadata.get("rowsUpdatedAt")
    try:
        source_updated = datetime.fromtimestamp(int(rows_updated), timezone.utc).isoformat()
    except (TypeError, ValueError, OSError):
        source_updated = None
    manifest = {
        "source": "DNP-ProyectosSGR / Socrata resource mzgh-shtp",
        "source_url": "https://www.datos.gov.co/Econom-a-y-Finanzas/DNP-ProyectosSGR/mzgh-shtp",
        "api_endpoint": SOURCE_URL,
        "metadata_endpoint": METADATA_URL,
        "license": "Creative Commons Attribution-ShareAlike 4.0 International",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_last_updated_utc": source_updated,
        "query": PARAMS,
        "selected_columns": FIELDS,
        "raw_response_sha256_not_persisted": raw_hash,
        "raw_response_bytes_not_persisted": len(source_response.content),
        "raw_response_rows": len(rows),
        "unique_bpin": total_project_count,
        "duplicate_bpin_groups": sum(len(group) > 1 for group in by_bpin.values()),
        "exact_duplicate_groups": exact_repeated_groups,
        "extra_duplicate_rows": extra_duplicate_rows,
        "conflicting_value_counts_by_field": dict(conflict_counts),
        "status_counts_unique_bpin": dict(sorted(status_counts.items())),
        "included_statuses": sorted(INCLUDED_STATES),
        "included_unique_projects_before_value_qa": len(included),
        "included_projects_analyzed": len(usable),
        "included_projects_missing_value": missing_value,
        "included_projects_negative_value": negative_value,
        "execution_values_outside_0_100_not_used": invalid_execution,
        "department_unambiguous_projects_analyzed": len(dept_eligible),
        "department_missing_or_ambiguous_projects_excluded": len(usable) - len(dept_eligible),
        "output_unit": "ValorTotal reportado por DNP; el companion no lo reinterpreta como asignación SGR ni pérdida.",
        "privacy": "No se conservan BPIN, nombres de proyectos ni filas individuales; el snapshot contiene únicamente agregados por categoría.",
    }
    (DATA / "source_quality_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def load_aggregates():
    with (DATA / "aggregated_sgr_projects.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    manifest = json.loads((DATA / "source_quality_manifest.json").read_text(encoding="utf-8"))
    for row in rows:
        for field in ("project_count", "value_total_reported", "project_share_pct", "value_share_pct"):
            row[field] = float(row[field])
    return rows, manifest


def summarize(rows, manifest):
    summary = {
        "source_last_updated_utc": manifest.get("source_last_updated_utc"),
        "retrieved_at_utc": manifest["retrieved_at_utc"],
        "raw_response_sha256_not_persisted": manifest["raw_response_sha256_not_persisted"],
        "raw_rows": manifest["raw_response_rows"],
        "unique_bpin_all_statuses": manifest["unique_bpin"],
        "included_unique_projects": manifest["included_projects_analyzed"],
        "included_statuses": manifest["included_statuses"],
        "department_project_coverage_pct": 100 * manifest["department_unambiguous_projects_analyzed"] / manifest["included_projects_analyzed"] if manifest["included_projects_analyzed"] else 0.0,
        "department_value_coverage_pct": None,
        "concentration": {},
        "interpretation": "Perfil descriptivo del universo público SGR; no identifica dependencia estadística, concentración de contratistas/compradores, pérdida ni exposición de un portafolio institucional.",
    }
    for dim in ("sector", "department_unambiguous", "executing_entity"):
        group = [r for r in rows if r["dimension"] == dim]
        vals = [r["value_share_pct"] for r in group]
        total_value = sum(r["value_total_reported"] for r in group)
        summary["concentration"][dim] = {
            "categories": len(group),
            "hhi_value_share_0_10000": sum(v * v for v in vals),
            "top5_value_share_pct": sum(sorted(vals, reverse=True)[:5]),
            "top_categories_by_value": [
                {"category": r["category"], "project_count": int(r["project_count"]), "value_total_reported": r["value_total_reported"], "value_share_pct": r["value_share_pct"]}
                for r in sorted(group, key=lambda x: x["value_total_reported"], reverse=True)[:5]
            ],
        }
    dep_total = sum(r["value_total_reported"] for r in rows if r["dimension"] == "department_unambiguous")
    value_total = sum(r["value_total_reported"] for r in rows if r["dimension"] == "sector")
    summary["department_value_coverage_pct"] = 100 * dep_total / value_total if value_total else 0.0
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def render(rows, summary):
    dims = [("sector", "Sector"), ("department_unambiguous", "Departamento con asignación única"), ("executing_entity", "Entidad ejecutora")]
    fig, axes = plt.subplots(1, 3, figsize=(15, 6), constrained_layout=True)
    colors = ["#176B87", "#498B72", "#D08C3F"]
    for ax, (dim, title), color in zip(axes, dims, colors):
        group = [r for r in rows if r["dimension"] == dim]
        group = sorted(group, key=lambda x: x["value_share_pct"], reverse=True)[:8]
        group = list(reversed(group))
        ax.barh([r["category"] for r in group], [r["value_share_pct"] for r in group], color=color)
        ax.set_title(title)
        ax.set_xlabel("Participación en ValorTotal reportado (%)")
        ax.grid(axis="x", alpha=.2)
        for y, r in enumerate(group):
            ax.text(r["value_share_pct"] + .3, y, f"{r['value_share_pct']:.1f}%", va="center", fontsize=8)
    fig.suptitle("Concentración descriptiva de proyectos públicos SGR por valor reportado\nSin inferir concentración de contratistas, pérdidas o dependencia", fontsize=13)
    RESULTS.mkdir(exist_ok=True)
    fig.savefig(RESULTS / "sgr_project_value_concentration.png", dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Consulta DNP/Datos Abiertos y actualiza el snapshot agregado minimizado.")
    args = parser.parse_args()
    if args.refresh:
        manifest = refresh_snapshot()
    else:
        manifest = json.loads((DATA / "source_quality_manifest.json").read_text(encoding="utf-8"))
    rows, manifest = load_aggregates()
    summary = summarize(rows, manifest)
    render(rows, summary)
    print(json.dumps({"refresh": args.refresh, "source_rows": manifest["raw_response_rows"], "unique_bpin": manifest["unique_bpin"], "included_projects": manifest["included_projects_analyzed"], "sector_hhi": summary["concentration"]["sector"]["hhi_value_share_0_10000"], "department_coverage_pct": summary["department_value_coverage_pct"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
