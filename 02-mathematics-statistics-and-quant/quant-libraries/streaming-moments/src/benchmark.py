"""Deterministic cancellation and representation audit; Decimal oracle."""

import csv
import json
import platform
import sys
import time
import tracemalloc
from decimal import Decimal, localcontext
from pathlib import Path
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.moments import Moments, summarize


def raw(x: list[float]) -> float:
    return sum(v * v for v in x) / len(x) - (sum(x) / len(x)) ** 2


def ordinary(x: list[float]) -> float:
    n = 0
    mean = 0.0
    m2 = 0.0
    for v in x:
        n += 1
        d = v - mean
        mean += d / n
        m2 += d * (v - mean)
    return m2 / n


def merged(x: list[float]) -> float:
    out = Moments()
    for start in range(0, len(x), 127):
        out = out.merge(summarize(x[start : start + 127]))
    return out.variance()


def oracle(x: list[float]) -> float:
    with localcontext() as ctx:
        ctx.prec = 80
        z = [Decimal.from_float(v) for v in x]
        mean = sum(z) / len(z)
        return float(sum((v - mean) ** 2 for v in z) / len(z))


def main() -> None:
    config = json.loads(Path("config.json").read_text())
    rows = []
    for n in config["sizes"]:
        for offset in config["offsets"]:
            x = [offset + float(i % 4) for i in range(n)]
            ref = oracle(x)
            for name, fn in [
                ("raw_moments", raw),
                ("numpy_two_pass", lambda a: float(np.var(a))),
                ("ordinary_welford", ordinary),
                ("shifted_stream", lambda a: summarize(iter(a)).variance()),
                ("shifted_merge127", merged),
            ]:
                fn(x)
                tracemalloc.start()
                t = time.perf_counter_ns()
                value = fn(x)
                elapsed = time.perf_counter_ns() - t
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                rows.append(
                    dict(
                        n=n,
                        offset=offset,
                        method=name,
                        variance=value,
                        oracle=ref,
                        abs_error=abs(value - ref),
                        intended_error=abs(value - 1.25),
                        ns=elapsed,
                        python_peak_bytes=peak,
                    )
                )
    out = Path("results")
    out.mkdir(exist_ok=True)
    with (out / "raw.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    normal = [r for r in rows if r["offset"] <= 1e12]
    summary = {
        "cases": len(rows),
        "max_error_representable": {
            m: max(r["abs_error"] for r in normal if r["method"] == m)
            for m in sorted({r["method"] for r in rows})
        },
        "representation_loss": [
            r for r in rows if r["offset"] == 1e16 and r["method"] == "shifted_stream"
        ],
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "processor": platform.processor(),
        },
        "timing_scope": "one warmed call with tracemalloc; diagnostic not speed claim; Python tracked allocations, not process RSS",
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    fig, ax = plt.subplots(figsize=(8, 4))
    for m in sorted({r["method"] for r in rows}):
        rr = [r for r in rows if r["n"] == config["sizes"][-1] and r["method"] == m]
        ax.plot(
            [str(r["offset"]) for r in rr],
            [max(r["abs_error"], 1e-18) for r in rr],
            "o-",
            label=m,
        )
    ax.set_yscale("log")
    ax.set_ylabel("Absolute error vs Decimal of float inputs (floor 1e-18)")
    ax.set_xlabel("Added offset; 1e16 already loses original increments")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "audit.png", dpi=150)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
