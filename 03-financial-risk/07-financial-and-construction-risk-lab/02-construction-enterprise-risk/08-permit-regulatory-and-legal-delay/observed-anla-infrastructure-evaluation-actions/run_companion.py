"""Aggregate ANLA infrastructure evaluation action date pairs without retaining IDs."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import math
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests

BASE = Path(__file__).resolve().parent
OUT = BASE / "results"
QUERY_URL = (
    "https://portalsig.anla.gov.co/publico/rest/services/PROYECTOS_ANLA/"
    "ProyectosANLA_Evaluacion/FeatureServer/2/query"
)
PARAMS = {
    "where": "sector=102",  # coded value documented by the layer: Infraestructura
    "outFields": "expediente,sector,num_act_ad,fec_act_ad,estado,radicado,fecha_radicado",
    "returnGeometry": "false",
    "resultRecordCount": 1000,
    "f": "json",
}
SOURCE_ITEM = "https://www.arcgis.com/home/item.html?id=fab4a3ec84de4b1c9549ce63b01a0524"


def percentile(values, p):
    if not values:
        return None
    ordered = sorted(values)
    return float(ordered[math.ceil(p * len(ordered)) - 1])


def date_text(milliseconds):
    if milliseconds is None:
        return None
    return datetime.fromtimestamp(milliseconds / 1000, timezone.utc).date().isoformat()


def main():
    response = requests.get(QUERY_URL, params=PARAMS, timeout=60)
    response.raise_for_status()
    payload_bytes = response.content
    payload = response.json()
    if payload.get("error"):
        raise RuntimeError(f"ArcGIS REST devolvió error: {payload['error']}")
    features = payload.get("features", [])
    if not features or not payload.get("fields"):
        raise ValueError("La consulta oficial no devolvió filas o esquema")
    source_hash = hashlib.sha256(payload_bytes).hexdigest()
    rows = [feature["attributes"] for feature in features]

    # La capa poligonal repite proyectos/actos por fragmento espacial. Deduplicar
    # la misma combinación evento antes de resumir, sin guardar identificadores.
    keys = ("expediente", "sector", "num_act_ad", "fec_act_ad", "estado", "radicado", "fecha_radicado")
    events = {tuple(row.get(key) for key in keys): row for row in rows}.values()
    events = list(events)
    if any(row.get("sector") != 102 for row in events):
        raise ValueError("El filtro de sector devolvió códigos distintos de Infraestructura (102)")

    projects = {}
    for row in events:
        case_id = row.get("expediente")
        current = projects.get(case_id)
        if current is None or (row.get("fec_act_ad") or 0) > (current.get("fec_act_ad") or 0):
            projects[case_id] = row

    lags = []
    missing_filing_date = 0
    negative_date_pairs = 0
    for row in events:
        filing, act = row.get("fecha_radicado"), row.get("fec_act_ad")
        if filing is None or act is None:
            missing_filing_date += 1
            continue
        lag = (act - filing) / 86_400_000
        if lag < 0:
            negative_date_pairs += 1
            continue
        lags.append((lag, row.get("estado") or "SIN_ESTADO"))

    if not lags:
        raise ValueError("No hay pares de fechas cronológicos para resumir")
    grouped = {}
    for lag, status in lags:
        grouped.setdefault(status, []).append(lag)
    status_rows = []
    for status, values in sorted(grouped.items()):
        status_rows.append({
            "estado_registrado": status,
            "pares_fecha_validos": len(values),
            "mediana_dias_calendario": float(statistics.median(values)),
            "p90_dias_calendario": percentile(values, 0.90),
            "maximo_dias_calendario": float(max(values)),
        })

    event_status = Counter(row.get("estado") or "SIN_ESTADO" for row in events)
    project_status = Counter(row.get("estado") or "SIN_ESTADO" for row in projects.values())
    action_dates = [row.get("fec_act_ad") for row in events if row.get("fec_act_ad")]
    filing_dates = [row.get("fecha_radicado") for row in events if row.get("fecha_radicado")]
    summary = {
        "source": SOURCE_ITEM,
        "service_layer": QUERY_URL,
        "query_sector_code": 102,
        "query_sector_label": "Infraestructura (código de dominio oficial)",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "response_sha256_ephemeral": source_hash,
        "raw_geometry_rows_received": len(rows),
        "deduplicated_project_action_date_rows": len(events),
        "unique_project_ids_count_only": len(projects),
        "event_rows_by_registered_status": dict(sorted(event_status.items())),
        "latest_record_status_by_project_count_only": dict(sorted(project_status.items())),
        "pairs_with_both_dates": len(events) - missing_filing_date,
        "negative_date_pairs_excluded": negative_date_pairs,
        "missing_filing_date_pairs_excluded": missing_filing_date,
        "valid_nonnegative_pairs": len(lags),
        "radicado_date_min": date_text(min(filing_dates)) if filing_dates else None,
        "radicado_date_max": date_text(max(filing_dates)) if filing_dates else None,
        "admin_act_date_min": date_text(min(action_dates)) if action_dates else None,
        "admin_act_date_max": date_text(max(action_dates)) if action_dates else None,
        "lag_days_median": float(statistics.median(value for value, _ in lags)),
        "lag_days_p90_nearest_rank": percentile([value for value, _ in lags], 0.90),
        "lag_days_max": float(max(value for value, _ in lags)),
        "lag_definition": "Calendar days between the paired FECHA_RADICADO and FEC_ACT_AD on each current layer row; not end-to-end review or permit duration.",
        "raw_project_identifiers_saved": False,
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    import csv
    with (OUT / "lag_summary_by_registered_status.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=status_rows[0].keys())
        writer.writeheader()
        writer.writerows(status_rows)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), constrained_layout=True)
    axes[0].bar(list(project_status), list(project_status.values()), color="#347c83")
    axes[0].set_title(f"Estado del último acto por proyecto (n={len(projects)})")
    axes[0].set_ylabel("Proyectos (conteo)")
    axes[0].tick_params(axis="x", rotation=25)
    axes[1].hist([value for value, _ in lags], bins=8, color="#cd8850", edgecolor="white")
    axes[1].axvline(statistics.median(value for value, _ in lags), color="#263b4a", linestyle="--", label="Mediana")
    axes[1].set_title(f"Radicado → acto administrativo (n={len(lags)} pares válidos)")
    axes[1].set_xlabel("Días calendario en el registro; no duración total del trámite")
    axes[1].set_ylabel("Filas evento deduplicadas")
    axes[1].legend(frameon=False)
    fig.savefig(OUT / "infrastructure_evaluation_action_dates.png", dpi=160)
    plt.close(fig)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
