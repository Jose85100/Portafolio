import csv
import json
import platform
import time
import tracemalloc
from pathlib import Path
from src.balancing import balanced_split, count_split, fixture
from src.splitter import leaked_components

CASES = {
    "equal": [3, 3, 3, 3],
    "skew": [1, 1, 1, 9],
    "mixed": [1, 2, 3, 10],
    "balanced": [2, 3, 7, 8],
    "giant": [1, 1, 1, 30],
}
RATIOS = [(1, 4), (1, 3), (1, 2), (2, 3), (3, 4)]


def measure(
    sizes: list[int], name: str, p: int, q: int, policy: str
) -> dict[str, object]:
    rows = fixture(sizes)
    method = balanced_split if policy == "exact" else count_split
    tracemalloc.start()
    start = time.perf_counter_ns()
    assignment = method(rows, p, q)
    elapsed = time.perf_counter_ns() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    mass = sum(v == "train" for v in assignment.values())
    return dict(
        case=name,
        policy=policy,
        numerator=p,
        denominator=q,
        rows=len(rows),
        groups=len(sizes),
        train_rows=mass,
        deviation_rows=abs(q * mass - p * len(rows)) / q,
        leaks=leaked_components(rows, assignment),
        elapsed_ns=elapsed,
        peak_bytes=peak,
    )


def main() -> None:
    out = Path("results/balancing30")
    out.mkdir(exist_ok=True)
    (out / "inputs.json").write_text(
        json.dumps(
            dict(cases=CASES, ratios=RATIOS, scale_group_counts=[10, 30, 60]), indent=2
        )
    )
    raw = [
        measure(sizes, name, p, q, policy)
        for name, sizes in CASES.items()
        for p, q in RATIOS
        for policy in ["count", "exact"]
    ]
    scales = [
        measure([i % 9 + 1 for i in range(k)], f"scale{k}", 1, 2, policy)
        for k in [10, 30, 60]
        for policy in ["count", "exact"]
    ]
    for filename, data in [("raw.csv", raw), ("scale.csv", scales)]:
        with (out / filename).open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)
    deltas = [
        float(raw[i]["deviation_rows"]) - float(raw[i + 1]["deviation_rows"])
        for i in range(0, len(raw), 2)
    ]
    summary = dict(
        python=platform.python_version(),
        platform=platform.platform(),
        comparisons=len(deltas),
        improved=sum(x > 0 for x in deltas),
        equal=sum(x == 0 for x in deltas),
        worse=sum(x < 0 for x in deltas),
        leaks=sum(int(r["leaks"]) for r in raw),
        mean_deviation={
            policy: sum(
                float(r["deviation_rows"]) for r in raw if r["policy"] == policy
            )
            / 25
            for policy in ["count", "exact"]
        },
        half=[r for r in raw if r["numerator"] == 1 and r["denominator"] == 2],
        scale=scales,
    )
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    body = ""
    for i, (name, sizes) in enumerate(CASES.items()):
        y = 75 + i * 60
        body += f'<text x="20" y="{y + 16}" font-size="16">{name}</text>'
        for j, policy in enumerate(["count", "exact"]):
            r = next(
                r
                for r in summary["half"]
                if r["case"] == name and r["policy"] == policy
            )
            value = float(r["deviation_rows"])
            body += f'<rect x="130" y="{y + j * 20}" width="{value * 22}" height="15" fill="{["#a96328", "#236b9b"][j]}"/><text x="{140 + value * 22}" y="{y + 13 + j * 20}" font-size="13">{value:g}</text>'
    (out / "balance.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="700" height="440"><rect width="700" height="440" fill="white"/><text x="20" y="26" font-size="20">Desviación absoluta (filas) respecto a N/2</text><text x="20" y="50" font-size="14">Naranja: número de grupos; azul: exacto por masa</text>'
        + body
        + '<text x="20" y="415" font-size="14">Componente gigante: desequilibrio irreducible, no fuga.</text></svg>'
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
