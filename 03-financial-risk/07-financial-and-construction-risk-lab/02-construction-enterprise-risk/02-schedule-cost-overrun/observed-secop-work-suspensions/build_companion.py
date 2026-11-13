"""Reproduce aggregate SECOP II suspension/resumption record counts."""
from datetime import date
from pathlib import Path
import hashlib
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import requests

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
API = "https://www.datos.gov.co/resource/u99c-7mfm.json"
LOWER = "2020-01-01T00:00:00"
UPPER = "2026-01-01T00:00:00"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refresh():
    params = {
        "$select": "date_extract_y(fecha_de_aprobacion) as year,tipo,count(*) as reported_rows",
        "$where": f'fecha_de_aprobacion >= "{LOWER}" AND fecha_de_aprobacion < "{UPPER}"',
        "$group": "year,tipo", "$order": "year,tipo"
    }
    response = requests.get(API, params=params, timeout=60)
    response.raise_for_status()
    rows = response.json()
    RESULTS.mkdir(parents=True, exist_ok=True)
    data_path = RESULTS / "annual_secop_suspension_records.csv"
    df = pd.DataFrame(rows).rename(columns={"year": "approval_year", "tipo": "event_type"})
    df["approval_year"] = pd.to_numeric(df.approval_year, errors="raise").astype(int)
    df["reported_rows"] = pd.to_numeric(df.reported_rows, errors="raise").astype(int)
    df = df.sort_values(["approval_year", "event_type"]).reset_index(drop=True)
    df.to_csv(data_path, index=False)
    manifest = {
        "source": "SECOP II - Suspensiones de Contratos, Colombia Compra Eficiente / Datos Abiertos Colombia",
        "source_url": "https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Suspensiones-de-Contratos/u99c-7mfm",
        "resource_id": "u99c-7mfm", "query": params,
        "retrieved_on": date.today().isoformat(), "source_rows_aggregated": int(df.reported_rows.sum()),
        "snapshot_row_count": int(len(df)), "sha256_aggregated_csv": sha256(data_path),
        "scope_note": "Counts raw source records by approval year and event type. Not distinct contracts or events; the endpoint contains exact duplicate rows.",
        "qa": {"six_years_2020_2025": sorted(df.approval_year.unique().tolist()) == list(range(2020, 2026)),
               "types_are_suspension_and_resumption": set(df.event_type.str.casefold()) == {"suspension", "reanudacion"},
               "counts_nonnegative": bool((df.reported_rows >= 0).all())}
    }
    (RESULTS / "source_quality_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


def build():
    data_path = RESULTS / "annual_secop_suspension_records.csv"
    manifest_path = RESULTS / "source_quality_manifest.json"
    if not data_path.exists() or not manifest_path.exists():
        raise FileNotFoundError("Faltan snapshots; ejecute el script con --refresh")
    manifest = json.loads(manifest_path.read_text())
    if sha256(data_path) != manifest["sha256_aggregated_csv"]:
        raise ValueError("El SHA-256 del snapshot agregado no coincide con el manifiesto")
    df = pd.read_csv(data_path)
    years = sorted(df.approval_year.unique().tolist())
    types = set(df.event_type.str.casefold())
    if years != list(range(2020, 2026)) or types != {"suspension", "reanudacion"}:
        raise ValueError("El snapshot debe contener 2020–2025 y ambos tipos de registro")
    if df.duplicated(["approval_year", "event_type"]).any() or (df.reported_rows < 0).any():
        raise ValueError("Claves anuales duplicadas o conteos inválidos")
    pivot = df.pivot(index="approval_year", columns="event_type", values="reported_rows").fillna(0)
    pivot = pivot.rename(columns={"Suspension": "Suspension", "Reanudacion": "Reanudacion"})
    fig, ax = plt.subplots(figsize=(9, 4.8), constrained_layout=True)
    pivot[["Suspension", "Reanudacion"]].plot(kind="bar", ax=ax, color=["#246a73", "#db9d47"])
    ax.set_title("SECOP II: registros reportados de suspensión y reanudación")
    ax.set_xlabel("Año de aprobación registrado")
    ax.set_ylabel("Filas reportadas en la fuente")
    ax.legend(["Suspensión", "Reanudación"], frameon=False)
    ax.tick_params(axis="x", rotation=0)
    fig.savefig(RESULTS / "secop_suspension_record_counts.png", dpi=160)
    plt.close(fig)
    summary = {"cutoff": manifest["retrieved_on"], "counts_by_year_and_type": df.to_dict(orient="records"),
               "total_reported_rows": int(df.reported_rows.sum()),
               "warning": "Raw source rows may duplicate contract events. Dataset is not filtered to public works, so no construction-only rate, suspension duration, delay or loss is estimated."}
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if "--refresh" in sys.argv:
        refresh()
    build()
