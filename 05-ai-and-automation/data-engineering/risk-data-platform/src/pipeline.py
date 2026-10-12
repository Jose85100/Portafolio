"""Deterministic risk-data publication with immutable snapshots.

The public API writes a complete run under ``runs/<run_id>/`` and only then
atomically replaces ``current.json``. Consumers must resolve that pointer;
they never read a mutable CSV/manifest pair.
"""
import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

FIELDS = ("loan_id", "as_of_date", "principal", "days_past_due", "status")
STATUSES = {"active", "closed", "default"}
SCHEMA_VERSION = "1.1"


def money(value):
    try:
        x = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("invalid principal")
    if not x.is_finite() or x < 0:
        raise ValueError("principal must be finite and nonnegative")
    return x.quantize(Decimal("0.01"))


def normalize(row):
    if set(row) != set(FIELDS):
        raise ValueError("schema mismatch")
    loan = row["loan_id"].strip()
    if not loan:
        raise ValueError("empty loan_id")
    try:
        day = date.fromisoformat(row["as_of_date"])
        dpd = int(row["days_past_due"])
    except (ValueError, TypeError):
        raise ValueError("invalid date or dpd")
    if dpd < 0 or str(dpd) != str(row["days_past_due"]).strip():
        raise ValueError("days_past_due must be a nonnegative integer")
    status = row["status"].strip().lower()
    if status not in STATUSES:
        raise ValueError("invalid status")
    principal = money(row["principal"])
    if status == "closed" and principal != 0:
        raise ValueError("closed loan must have zero principal")
    return {"loan_id": loan, "as_of_date": day.isoformat(),
            "principal": str(principal), "days_past_due": dpd, "status": status}


def atomic_write(path, content):
    """Durably replace one file. Used for the activation pointer only."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".tmp-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def _csv_rows(path):
    existing = {}
    if path.exists():
        with path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                item = normalize(row)
                existing[(item["loan_id"], item["as_of_date"])] = item
    return existing


def _read_source(source, reject_path):
    incoming, errors = {}, []
    with Path(source).open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or set(reader.fieldnames) != set(FIELDS) or len(reader.fieldnames) != len(FIELDS):
            raise ValueError("input columns do not match contract")
        for line, row in enumerate(reader, start=2):
            try:
                item = normalize(row)
                key = (item["loan_id"], item["as_of_date"])
                if key in incoming and incoming[key] != item:
                    raise ValueError("conflicting duplicate in source")
                incoming[key] = item
            except (ValueError, AttributeError, TypeError) as exc:
                errors.append({"line": line, "error": str(exc)})
    if errors:
        if reject_path is not None:
            atomic_write(reject_path, json.dumps(errors, indent=2) + "\n")
        raise ValueError(f"{len(errors)} invalid source records; no output committed")
    return incoming


def _body(rows):
    return ",".join(FIELDS) + "\n" + "".join(
        ",".join(str(item[k]) for k in FIELDS) + "\n" for item in rows
    )


def _load_current(snapshot_root):
    pointer = Path(snapshot_root) / "current.json"
    if not pointer.exists():
        return {}, None
    reference = json.loads(pointer.read_text(encoding="utf-8"))
    csv_path = Path(snapshot_root) / reference["csv"]
    manifest_path = Path(snapshot_root) / reference["manifest"]
    if not csv_path.exists() or not manifest_path.exists():
        raise ValueError("current snapshot pointer references a missing artifact")
    actual = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if actual != reference["sha256"] or manifest.get("sha256") != actual:
        raise ValueError("current snapshot hashes do not match its pointer and manifest")
    return _csv_rows(csv_path), reference


def publish_snapshot(source, snapshot_root, reject_path=None, run_id=None):
    """Publish an immutable run and atomically activate it.

    ``runs/<run_id>`` is created completely before ``current.json`` changes.
    Replaying identical data is idempotent: it reuses the content-addressed id.
    """
    source, snapshot_root = Path(source), Path(snapshot_root)
    existing, _ = _load_current(snapshot_root)
    incoming = _read_source(source, reject_path)
    merged = dict(existing)
    merged.update(incoming)
    rows = [merged[k] for k in sorted(merged)]
    body = _body(rows)
    payload = body.encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    run_id = run_id or f"sha256-{digest[:20]}"
    if not run_id.replace("-", "").replace("_", "").isalnum():
        raise ValueError("run_id may contain only letters, digits, hyphens and underscores")
    total = sum((Decimal(x["principal"]) for x in rows), Decimal("0.00"))
    metrics = {
        "schema_version": SCHEMA_VERSION, "run_id": run_id,
        "source_rows": len(incoming), "published_rows": len(rows),
        "new_keys": len(set(incoming) - set(existing)),
        "updated_keys": sum(existing.get(k) != v for k, v in incoming.items() if k in existing),
        "total_principal": str(total), "sha256": digest,
        "min_as_of_date": min((x["as_of_date"] for x in rows), default=None),
        "max_as_of_date": max((x["as_of_date"] for x in rows), default=None),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    runs = snapshot_root / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    final_dir = runs / run_id
    if final_dir.exists():
        prior = final_dir / "manifest.json"
        if not prior.exists() or json.loads(prior.read_text(encoding="utf-8")).get("sha256") != digest:
            raise ValueError("run_id already exists with different content")
    else:
        temp_dir = runs / f".pending-{uuid.uuid4().hex}"
        try:
            temp_dir.mkdir()
            (temp_dir / "curated.csv").write_bytes(payload)
            (temp_dir / "manifest.json").write_text(json.dumps(metrics, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            os.replace(temp_dir, final_dir)
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    csv_path, manifest_path = final_dir / "curated.csv", final_dir / "manifest.json"
    stored = json.loads(manifest_path.read_text(encoding="utf-8"))
    if hashlib.sha256(csv_path.read_bytes()).hexdigest() != stored["sha256"]:
        raise ValueError("snapshot verification failed; pointer was not updated")
    reference = {"run_id": run_id, "csv": str(csv_path.relative_to(snapshot_root)),
                 "manifest": str(manifest_path.relative_to(snapshot_root)), "sha256": digest}
    atomic_write(snapshot_root / "current.json", json.dumps(reference, sort_keys=True, indent=2) + "\n")
    # Return this invocation's reconciliation metrics. The immutable manifest
    # remains the evidence for the snapshot's first publication.
    return metrics


def run(source, output, manifest, reject_path=None):
    """Compatibility adapter. New consumers must use :func:`publish_snapshot`."""
    output, manifest = Path(output), Path(manifest)
    if Path(source).resolve() == output.resolve():
        raise ValueError("source and output must differ")
    snapshot_root = output.parent / ".risk-snapshots"
    metrics = publish_snapshot(source, snapshot_root, reject_path)
    reference = json.loads((snapshot_root / "current.json").read_text(encoding="utf-8"))
    atomic_write(output, (snapshot_root / reference["csv"]).read_text(encoding="utf-8"))
    atomic_write(manifest, (snapshot_root / reference["manifest"]).read_text(encoding="utf-8"))
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--snapshot-root", required=True)
    parser.add_argument("--rejects")
    args = parser.parse_args()
    print(json.dumps(publish_snapshot(args.source, args.snapshot_root, args.rejects), indent=2))
