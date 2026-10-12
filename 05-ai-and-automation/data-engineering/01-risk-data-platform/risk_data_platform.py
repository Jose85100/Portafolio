"""Deterministic D+1 loan snapshot and reconciliation."""
import csv
import datetime as dt
import decimal
import json
import os
import tempfile
from collections import defaultdict
from pathlib import Path

D = decimal.Decimal
FIELDS = ("loan_id", "as_of_date", "principal", "days_past_due")

def build_snapshot(source, as_of):
    target = dt.date.fromisoformat(as_of)
    latest = {}
    with open(source, newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if not set(FIELDS).issubset(reader.fieldnames or []):
            raise ValueError("missing required columns")
        for row in reader:
            date = dt.date.fromisoformat(row["as_of_date"])
            if date > target:
                continue
            key = row["loan_id"].strip()
            if not key:
                raise ValueError("empty loan_id")
            balance = D(row["principal"])
            dpd = int(row["days_past_due"])
            if not balance.is_finite() or balance < 0 or dpd < 0:
                raise ValueError("invalid loan metrics")
            candidate = (date, balance, dpd)
            if key in latest and latest[key][0] == date and latest[key] != candidate:
                raise ValueError("conflicting records for same loan/date")
            if key not in latest or date > latest[key][0]:
                latest[key] = candidate
    result = []
    for key, (date, balance, dpd) in sorted(latest.items()):
        result.append({"loan_id": key, "as_of_date": date.isoformat(),
                       "principal": str(balance), "days_past_due": dpd,
                       "bucket": "current" if dpd == 0 else ("1-30" if dpd <= 30 else "31+")})
    total = sum((D(x["principal"]) for x in result), D(0))
    return {"as_of": target.isoformat(), "loan_count": len(result),
            "principal_total": str(total), "records": result}

def publish_atomic(payload, destination):
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".snapshot-", suffix=".json", delete=False) as f:
            temp = f.name
            json.dump(payload, f, indent=2, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if temp and os.path.exists(temp):
            os.unlink(temp)
