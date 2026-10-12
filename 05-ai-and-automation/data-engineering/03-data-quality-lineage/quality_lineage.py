"""Declarative CSV validation and immutable evidence manifest."""
import csv
import hashlib
import json
from pathlib import Path

def validate_csv(path, rules):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = set(reader.fieldnames or [])
    violations = []
    for rule in rules:
        field, operation = rule["field"], rule["op"]
        if field not in fields:
            raise ValueError("unknown field: " + field)
        if operation not in ("not_null", "unique", "min", "max"):
            raise ValueError("unknown rule: " + operation)
        seen = set()
        for i, row in enumerate(rows, start=2):
            value = row[field]
            failed = False
            if operation == "not_null":
                failed = value is None or not value.strip()
            elif operation == "unique":
                failed = value in seen
                seen.add(value)
            elif operation in ("min", "max"):
                try:
                    v = float(value)
                    import math
                    failed = not math.isfinite(v) or (v < float(rule["value"]) if operation == "min" else v > float(rule["value"]))
                except (TypeError, ValueError):
                    failed = True
            if failed:
                violations.append({"line": i, "field": field, "rule": operation})
    return {"rows": len(rows), "passed": not violations, "violations": violations}

def evidence(path, result):
    content = Path(path).read_bytes()
    return {"source": Path(path).name, "sha256": hashlib.sha256(content).hexdigest(),
            "bytes": len(content), "validation": result}

def save_manifest(manifest, destination):
    Path(destination).write_text(json.dumps(manifest, sort_keys=True, indent=2), encoding="utf-8")
