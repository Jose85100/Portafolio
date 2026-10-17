import csv
import json
from pathlib import Path
from collections import defaultdict

def report():
    root = Path(__file__).resolve().parents[1] / "results"
    data = list(csv.DictReader((root/"raw.csv").open()))
    groups = defaultdict(list)
    for row in data:
        groups[(row["regime"], row["method"])].append(row)
    summary = [{"regime": k[0], "method": k[1], "n": len(v),
                "coverage": sum(float(x["coverage"]) for x in v)/len(v),
                "worst_group": sum(float(x["worst_group"]) for x in v)/len(v),
                "width": sum(float(x["width"]) for x in v)/len(v)}
               for k,v in sorted(groups.items())]
    (root/"summary.json").write_text(json.dumps(summary, indent=2))
    return summary

if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
