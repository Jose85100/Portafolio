"""Turn observed ICETEX portfolio snapshots into exposure-count weighted signals.

These are STOCK prevalence rates (not PD, default flows or balance weighted rates).
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def signals(records):
    aggregate = defaultdict(lambda: {"loans": 0, "late": 0, "rows": 0})
    for row in records:
        if row.get("evidencia") != "OBSERVADO_AGREGADO":
            raise ValueError("Only validated observed aggregate records are permitted")
        date_key = row["fecha_corte"]
        phase = row["epoca_cartera"]
        total, late = int(row["creditos_total"]), int(row["creditos_mora_mayor_90d"])
        if total <= 0 or late < 0 or late > total:
            raise ValueError("Invalid observed credit counts")
        for key in ((date_key, phase), (date_key, "ALL_PHASES")):
            aggregate[key]["loans"] += total
            aggregate[key]["late"] += late
            aggregate[key]["rows"] += 1
    return [
        {"fecha_corte": d, "epoca_cartera": phase,
         "creditos_total": counts["loans"],
         "creditos_mora_mayor_90d": counts["late"],
         "share_creditos_mora_mayor_90d": counts["late"] / counts["loans"],
         "contributing_segments": counts["rows"],
         "evidence": "OBSERVED_ICETEX_STOCK_NOT_PD"}
        for (d, phase), counts in sorted(aggregate.items())
    ]


def run(source, output):
    with Path(source).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    result = signals(rows)
    if not result:
        raise ValueError("No validated observations")
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result[0]))
        writer.writeheader()
        writer.writerows(result)
    return {"periods": len({x["fecha_corte"] for x in result}),
            "rows": len(result), "output": str(out),
            "source_observations": len(rows),
            "metric": "count_weighted_arrears_stock_share_not_PD"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.source, args.output), indent=2))
