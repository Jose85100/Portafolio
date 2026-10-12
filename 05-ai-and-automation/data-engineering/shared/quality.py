"""Declarative data quality checks. Standard library only."""
from collections import Counter
from decimal import Decimal, InvalidOperation

def evaluate(rows, rules):
    """Return deterministic findings; no silent coercion."""
    findings = []
    for rule in rules:
        name, field, kind = rule["name"], rule.get("field"), rule["type"]
        if kind == "unique":
            seen = set()
            for i, row in enumerate(rows):
                key = tuple(row.get(x) for x in rule["fields"])
                if key in seen:
                    findings.append({"rule": name, "row": i, "reason": "duplicate"})
                seen.add(key)
        elif kind == "not_null":
            for i, row in enumerate(rows):
                if row.get(field) is None or str(row.get(field)).strip() == "":
                    findings.append({"rule": name, "row": i, "reason": "missing"})
        elif kind == "range":
            low, high = Decimal(str(rule["min"])), Decimal(str(rule["max"]))
            for i, row in enumerate(rows):
                try:
                    v = Decimal(str(row.get(field)))
                    if not v.is_finite() or not low <= v <= high:
                        raise InvalidOperation()
                except (InvalidOperation, ValueError, TypeError):
                    findings.append({"rule": name, "row": i, "reason": "outside_range"})
        elif kind == "allowed":
            allowed = set(rule["values"])
            for i, row in enumerate(rows):
                if row.get(field) not in allowed:
                    findings.append({"rule": name, "row": i, "reason": "not_allowed"})
        else:
            raise ValueError("unsupported rule: " + kind)
    counts = dict(sorted(Counter(f["rule"] for f in findings).items()))
    return {"passed": not findings, "evaluated_rows": len(rows),
            "violations": findings, "violations_by_rule": counts}
