"""Profile full SFC loan-stock panel without treating stock arrears as PD."""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

KEY = ("TIPO_ENTIDAD", "CODIGO_ENTIDAD", "FECHA_CORTE", "UNICAP", "RENGLON")
BALANCE = "(1) Saldo de la cartera a la fecha de corte del reporte"
CURRENT = "(2) Vigente"


def inspect(path):
    counts = Counter()
    fingerprints = defaultdict(set)
    duplicate_examples = []
    dates = []
    products = Counter()
    invalid = Counter()
    total = 0
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not set(KEY + (BALANCE, CURRENT, "DESCRIP_UC")).issubset(reader.fieldnames or []):
            raise ValueError("Unexpected SFC source schema")
        for row in reader:
            total += 1
            key = tuple(row[x] for x in KEY)
            counts[key] += 1
            fingerprints[key].add(tuple(row.items()))
            products[row["DESCRIP_UC"]] += 1
            try:
                dates.append(datetime.strptime(row["FECHA_CORTE"], "%d/%m/%Y").date())
                balance = float(row[BALANCE])
                current = float(row[CURRENT])
                if balance < 0 or current < 0:
                    invalid["negative_balance"] += 1
                if current > balance + max(1.0, balance * 1e-8):
                    invalid["current_exceeds_total"] += 1
            except (TypeError, ValueError):
                invalid["invalid_numerics_or_date"] += 1
    duplicate_keys = sum(x > 1 for x in counts.values())
    return {
        "rows": total,
        "date_min": min(dates).isoformat() if dates else None,
        "date_max": max(dates).isoformat() if dates else None,
        "unique_keys": len(counts),
        "duplicate_business_keys": duplicate_keys,
        "extra_duplicate_rows": sum(x - 1 for x in counts.values()),
        "conflicting_duplicate_keys": sum(len(fingerprints[k]) > 1 for k in counts if counts[k] > 1),
        "quality_flags": dict(invalid),
        "product_codes": len(products),
        "top_products": products.most_common(12),
        "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        "status": "PROFILED_NOT_CLEARED",
        "critical_limitation": "Hierarchical subrows overlap; do not sum all products or arrears buckets. Stock proportions are NOT individual PD.",
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    result = inspect(args.file)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
