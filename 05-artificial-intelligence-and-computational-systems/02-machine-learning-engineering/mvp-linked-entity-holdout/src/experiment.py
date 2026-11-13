import csv
import json
import platform
import time
import tracemalloc
from dataclasses import asdict
from pathlib import Path
from src.splitter import Record, split, leaked_components


def main() -> None:
    out = Path("results")
    out.mkdir(exist_ok=True)
    rows = []
    for i in range(12):
        rows += [
            Record(f"r{i:02}a", (f"a{i}",)),
            Record(f"r{i:02}b", (f"a{i}", f"b{i}")),
            Record(f"r{i:02}c", (f"b{i}",)),
        ]
    (out / "inputs.json").write_text(json.dumps([asdict(r) for r in rows], indent=2))
    raw = []
    for seed in range(12):
        for policy in ["row", "primary", "component"]:
            tracemalloc.start()
            start = time.perf_counter_ns()
            assignment = split(rows, policy, seed)
            elapsed = time.perf_counter_ns() - start
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            raw.append(
                dict(
                    seed=seed,
                    policy=policy,
                    leaked=leaked_components(rows, assignment),
                    train=sum(v == "train" for v in assignment.values()),
                    elapsed_ns=elapsed,
                    peak_bytes=peak,
                )
            )
    with (out / "raw.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(raw[0]))
        writer.writeheader()
        writer.writerows(raw)
    summary = {
        policy: dict(
            leaked_total=sum(int(r["leaked"]) for r in raw if r["policy"] == policy),
            component_opportunities=144,
            train_min=min(int(r["train"]) for r in raw if r["policy"] == policy),
            train_max=max(int(r["train"]) for r in raw if r["policy"] == policy),
            mean_ns=sum(int(r["elapsed_ns"]) for r in raw if r["policy"] == policy)
            / 12,
            peak_bytes=max(int(r["peak_bytes"]) for r in raw if r["policy"] == policy),
        )
        for policy in ["row", "primary", "component"]
    }
    (out / "summary.json").write_text(
        json.dumps(
            dict(
                python=platform.python_version(),
                platform=platform.platform(),
                results=summary,
            ),
            indent=2,
        )
    )
    bars = ""
    for i, (name, s) in enumerate(summary.items()):
        width = 350 * int(s["leaked_total"]) / 144
        bars += f'<text x="25" y="{90 + i * 65}" font-size="18">{name}</text><rect x="150" y="{70 + i * 65}" width="{width}" height="30" fill="#266a9f"/><text x="{165 + width}" y="{92 + i * 65}" font-size="17">{s["leaked_total"]}/144</text>'
    (out / "leakage.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="650" height="310"><rect width="650" height="310" fill="white"/><text x="25" y="30" font-size="20">Componentes cortados: 12 seeds × 12 grupos</text>'
        + bars
        + '<text x="25" y="285" font-size="14">Sintético; menos cortes no demuestra mejor predicción.</text></svg>'
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
