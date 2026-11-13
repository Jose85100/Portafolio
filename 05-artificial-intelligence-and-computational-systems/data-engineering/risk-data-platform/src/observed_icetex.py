"""Publish observed aggregate ICETEX credit snapshots with immutable evidence."""
import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
import tempfile
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "03-financial-risk/01-credit-risk/observed-data-proxies/src"))
from observed_portfolio import run as build_observed  # noqa: E402

FIELDS = (
    "fecha_corte", "departamento", "epoca_cartera", "creditos_al_dia",
    "creditos_con_mora", "creditos_total", "creditos_mora_mayor_90d",
    "proporcion_mora_mayor_90d", "proporcion_cualquier_mora",
    "indicador_cartera_vencida_fuente", "evidencia", "es_pd_individual",
)
KEY = ("fecha_corte", "departamento", "epoca_cartera")


def _decimal(value, name):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValueError(f"invalid {name}")
    if not number.is_finite():
        raise ValueError(f"nonfinite {name}")
    return number


def normalize(row):
    if set(row) != set(FIELDS):
        raise ValueError("schema mismatch")
    cut = date.fromisoformat(row["fecha_corte"]).isoformat()
    department = row["departamento"].strip()
    phase = row["epoca_cartera"].strip().upper()
    if not department or phase not in {"ESTUDIOS", "AMORTIZACION"}:
        raise ValueError("invalid department or phase")
    counts = {}
    for field in ("creditos_al_dia", "creditos_con_mora", "creditos_total", "creditos_mora_mayor_90d"):
        value = _decimal(row[field], field)
        if value < 0 or value != value.to_integral_value():
            raise ValueError(f"{field} must be a nonnegative integer")
        counts[field] = int(value)
    total = counts["creditos_total"]
    if total <= 0:
        raise ValueError("creditos_total must be positive")
    if counts["creditos_al_dia"] + counts["creditos_con_mora"] + counts["creditos_mora_mayor_90d"] != total:
        raise ValueError("credit counts do not reconcile")
    p90 = _decimal(row["proporcion_mora_mayor_90d"], "proporcion_mora_mayor_90d")
    pany = _decimal(row["proporcion_cualquier_mora"], "proporcion_cualquier_mora")
    if abs(p90 - Decimal(counts["creditos_mora_mayor_90d"]) / total) > Decimal("1e-12"):
        raise ValueError("90-day delinquency share does not reconcile")
    if abs(pany - Decimal(counts["creditos_con_mora"] + counts["creditos_mora_mayor_90d"]) / total) > Decimal("1e-12"):
        raise ValueError("any-delinquency share does not reconcile")
    if row["evidencia"] != "OBSERVADO_AGREGADO" or row["es_pd_individual"].lower() != "false":
        raise ValueError("source must remain labeled as observed aggregate, not individual PD")
    indicator = row["indicador_cartera_vencida_fuente"].strip()
    if indicator:
        _decimal(indicator, "indicador_cartera_vencida_fuente")
    return {
        "fecha_corte": cut, "departamento": department, "epoca_cartera": phase,
        **{field: counts[field] for field in counts},
        "proporcion_mora_mayor_90d": str(p90),
        "proporcion_cualquier_mora": str(pany),
        "indicador_cartera_vencida_fuente": indicator,
        "evidencia": "OBSERVADO_AGREGADO", "es_pd_individual": False,
    }


def atomic_write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".tmp-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def _read_csv(path):
    records = {}
    with Path(path).open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or set(reader.fieldnames) != set(FIELDS) or len(reader.fieldnames) != len(FIELDS):
            raise ValueError("input columns do not match observed ICETEX contract")
        for row in reader:
            item = normalize(row)
            key = tuple(item[field] for field in KEY)
            if key in records:
                raise ValueError(f"duplicate observed grain: {key}")
            records[key] = item
    if not records:
        raise ValueError("no complete observed records to publish")
    return records


def _load_current(root):
    pointer = Path(root) / "current.json"
    if not pointer.exists():
        return {}
    ref = json.loads(pointer.read_text(encoding="utf-8"))
    csv_path = Path(root) / ref["csv"]
    manifest_path = Path(root) / ref["manifest"]
    if not csv_path.exists() or not manifest_path.exists():
        raise ValueError("current pointer references a missing artifact")
    digest = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if digest != ref["sha256"] or digest != manifest.get("sha256"):
        raise ValueError("current source snapshot hash mismatch")
    return _read_csv(csv_path)


def publish_snapshot(curated_csv, source_manifest_path, snapshot_root):
    curated_csv, source_manifest_path, root = Path(curated_csv), Path(source_manifest_path), Path(snapshot_root)
    source = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    if source.get("quality_status") != "COMPLETE_CUTS_ONLY_WITH_EXPLICIT_QUARANTINE":
        raise ValueError("source manifest does not confirm complete-cut quarantine")
    records = _read_csv(curated_csv)
    previous = _load_current(root)
    rows = [records[key] for key in sorted(records)]
    payload = (",".join(FIELDS) + "\n" + "".join(
        ",".join(str(row[field]) for field in FIELDS) + "\n" for row in rows)).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    run_id = "sha256-" + digest[:20]
    created_at = datetime.now(timezone.utc).isoformat()
    metrics = {
        "schema_version": "2.0", "run_id": run_id,
        "provider": "ICETEX", "dataset": source["dataset"],
        "source_url": source["source_url"], "source_last_updated": source["source_last_updated"],
        "source_snapshot_sha256": source["source_snapshot_sha256"],
        "source_extracted_at": source["extracted_at"],
        "source_rows": source["source_rows"], "source_validated_rows": source["validated_rows"],
        "source_rejected_rows": source["rejected_rows"], "rejected_cuts": source["rejected_cuts"],
        "valid_rows_excluded_with_rejected_cuts": source["valid_rows_excluded_with_rejected_cuts"],
        "published_rows": len(rows),
        "new_keys": len(set(records) - set(previous)),
        "updated_keys": sum(previous.get(key) != row for key, row in records.items() if key in previous),
        "removed_keys": len(set(previous) - set(records)),
        "grain": "fecha_corte x departamento x epoca_cartera",
        "evidence": "observed public aggregate; not individual PD, transition, LGD or ECL",
        "sha256": digest, "created_at": created_at,
        "min_as_of_date": min(row["fecha_corte"] for row in rows),
        "max_as_of_date": max(row["fecha_corte"] for row in rows),
    }
    runs = root / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    final_dir = runs / run_id
    if not final_dir.exists():
        pending = runs / f".pending-{uuid.uuid4().hex}"
        pending.mkdir()
        try:
            (pending / "curated.csv").write_bytes(payload)
            (pending / "manifest.json").write_text(json.dumps(metrics, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            os.replace(pending, final_dir)
        finally:
            if pending.exists():
                shutil.rmtree(pending)
    stored = json.loads((final_dir / "manifest.json").read_text(encoding="utf-8"))
    if hashlib.sha256((final_dir / "curated.csv").read_bytes()).hexdigest() != stored["sha256"]:
        raise ValueError("published snapshot verification failed")
    pointer = {"run_id": run_id, "csv": str((final_dir / "curated.csv").relative_to(root)),
               "manifest": str((final_dir / "manifest.json").relative_to(root)), "sha256": digest}
    atomic_write(root / "current.json", json.dumps(pointer, sort_keys=True, indent=2) + "\n")
    return metrics


def run(as_of, snapshot_root, source_json=None, source_last_updated=None):
    with tempfile.TemporaryDirectory(prefix="icetex-source-") as work:
        source_output = Path(work) / "source"
        source_manifest = build_observed(as_of, source_output, source_json=source_json,
                                         source_last_updated=source_last_updated)
        return publish_snapshot(source_output / "delinquency_observed.csv",
                                source_output / "manifest.json", snapshot_root)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--snapshot-root", required=True)
    parser.add_argument("--source-json", help="Frozen source snapshot; omit to query the current API")
    parser.add_argument("--source-last-updated", help="Date shown by the source catalog (YYYY-MM-DD)")
    args = parser.parse_args()
    print(json.dumps(run(date.fromisoformat(args.as_of), args.snapshot_root,
                         args.source_json, args.source_last_updated), indent=2))
