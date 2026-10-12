"""Deterministic incremental risk data pipeline (Python standard library only)."""
import argparse
import csv
import hashlib
import json
import os
import tempfile
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

FIELDS = ("loan_id", "as_of_date", "principal", "days_past_due", "status")
STATUSES = {"active", "closed", "default"}
SCHEMA_VERSION = "1.0"

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

def run(source, output, manifest, reject_path=None):
    """Upsert by (loan_id, as_of_date). Reject bad rows; fail on key conflicts."""
    source, output, manifest = map(Path, (source, output, manifest))
    if source.resolve() == output.resolve():
        raise ValueError("source and output must differ")
    existing = {}
    if output.exists():
        with output.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                item = normalize(row)
                existing[(item["loan_id"], item["as_of_date"])] = item
    errors = []
    incoming = {}
    with source.open(newline="", encoding="utf-8-sig") as f:
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
    merged = dict(existing)
    merged.update(incoming)
    rows = [merged[k] for k in sorted(merged)]
    body = ",".join(FIELDS) + "\n"
    for item in rows:
        body += ",".join(str(item[k]) for k in FIELDS) + "\n"
    payload = body.encode("utf-8")
    total = sum((Decimal(x["principal"]) for x in rows), Decimal("0.00"))
    metrics = {"schema_version": SCHEMA_VERSION, "source_rows": len(incoming),
               "published_rows": len(rows), "new_keys": len(set(incoming)-set(existing)),
               "updated_keys": sum(existing.get(k) != v for k, v in incoming.items() if k in existing),
               "total_principal": str(total), "sha256": hashlib.sha256(payload).hexdigest(),
               "min_as_of_date": min((x["as_of_date"] for x in rows), default=None),
               "max_as_of_date": max((x["as_of_date"] for x in rows), default=None)}
    # Publication is per-file atomic, not a distributed two-phase transaction.
    atomic_write(output, body)
    atomic_write(manifest, json.dumps(metrics, sort_keys=True, indent=2) + "\n")
    return metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--rejects")
    args = parser.parse_args()
    print(json.dumps(run(args.source, args.output, args.manifest, args.rejects), indent=2))
