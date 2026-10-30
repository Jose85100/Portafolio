"""Scaling sensitivity and explicit overflow/underflow outcomes."""

import csv
import json
import math
import platform
import statistics
import sys
import time
import tracemalloc
from decimal import Decimal, localcontext
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from src.moments import summarize
from src.scaled import scaled_moments


def oracle(x: list[float]) -> float:
    with localcontext() as c:
        c.prec = 80
        z = [Decimal.from_float(v) for v in x]
        m = sum(z) / len(z)
        return float((sum((v - m) ** 2 for v in z) / len(z)).sqrt())


def main() -> None:
    config = json.loads(Path("config_scale.json").read_text())
    rows = []
    for n in config["sizes"]:
        for unit in config["units"]:
            x = [unit * (1 + i % 4) for i in range(n)]
            ref = oracle(x)
            e = math.frexp(unit)[1]
            for delta in config["exponent_deltas"]:
                exponent = e + delta
                if not -1074 <= exponent <= 1023:
                    continue

                def fn():
                    return scaled_moments(iter(x), exponent)

                out = fn()
                times = []
                for _ in range(config["repeats"]):
                    t = time.perf_counter_ns()
                    fn()
                    times.append(time.perf_counter_ns() - t)
                tracemalloc.start()
                fn()
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                rows.append(
                    dict(
                        n=n,
                        unit=unit,
                        method="scaled",
                        exponent=exponent,
                        delta=delta,
                        status=out.status,
                        variance=out.variance,
                        std=out.std,
                        oracle_std=ref,
                        relative_std_error=None
                        if out.std is None
                        else abs(out.std / ref - 1),
                        median_ns=statistics.median(times),
                        python_peak_bytes=peak,
                    )
                )
            for name, fn in [
                ("kernel29", lambda: summarize(x).variance()),
                ("numpy_two_pass", lambda: float(np.var(x))),
            ]:
                times = []
                with np.errstate(all="ignore"):
                    for _ in range(config["repeats"]):
                        t = time.perf_counter_ns()
                        var = fn()
                        times.append(time.perf_counter_ns() - t)
                sd = math.sqrt(var)
                valid = math.isfinite(sd) and (sd != 0 or ref == 0)
                rows.append(
                    dict(
                        n=n,
                        unit=unit,
                        method=name,
                        exponent=None,
                        delta=None,
                        status="ok" if valid else "nonfinite_or_lost",
                        variance=var if math.isfinite(var) else None,
                        std=sd if math.isfinite(sd) else None,
                        oracle_std=ref,
                        relative_std_error=abs(sd / ref - 1)
                        if math.isfinite(sd)
                        else None,
                        median_ns=statistics.median(times),
                        python_peak_bytes=None,
                    )
                )
            times = []
            for _ in range(config["repeats"]):
                t = time.perf_counter_ns()
                normalized = np.ldexp(np.asarray(x), -e)
                sd = math.ldexp(math.sqrt(float(np.var(normalized))), e)
                times.append(time.perf_counter_ns() - t)
            rows.append(
                dict(
                    n=n,
                    unit=unit,
                    method="numpy_scaled_sd",
                    exponent=e,
                    delta=0,
                    status="sd_available",
                    variance=None,
                    std=sd,
                    oracle_std=ref,
                    relative_std_error=abs(sd / ref - 1),
                    median_ns=statistics.median(times),
                    python_peak_bytes=None,
                )
            )
    path = Path("results")
    with (path / "scale_raw.csv").open("w") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    chosen = [r for r in rows if r["method"] == "scaled" and r["delta"] == 0]
    summary = dict(
        rows=len(rows),
        chosen_cases=len(chosen),
        chosen_statuses={
            s: sum(r["status"] == s for r in chosen)
            for s in {r["status"] for r in chosen}
        },
        chosen_max_relative_sd_error=max(r["relative_std_error"] for r in chosen),
        baseline_failures={
            m: sum(r["status"] != "ok" for r in rows if r["method"] == m)
            for m in ["kernel29", "numpy_two_pass"]
        },
        environment=dict(
            python=sys.version,
            platform=platform.platform(),
            processor=platform.processor(),
            numpy=np.__version__,
        ),
        timing="5 calls median; no tracemalloc during timing; memory separate Python allocations only, not RSS; no claim of throughput improvement",
    )
    (path / "scale_summary.json").write_text(json.dumps(summary, indent=2))
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for unit in config["units"]:
        rr = [
            r
            for r in rows
            if r["unit"] == unit and r["n"] == 4096 and r["method"] == "scaled"
        ]
        axes[0].plot(
            [r["delta"] for r in rr],
            [r["std"] is not None for r in rr],
            "o-",
            label=str(unit),
        )
    axes[0].set(
        xlabel="Exponent delta from frexp(unit)",
        ylabel="SD returned (1=yes)",
        ylim=(-0.1, 1.1),
    )
    axes[0].legend(title="unit")
    for m in ["scaled", "kernel29", "numpy_two_pass", "numpy_scaled_sd"]:
        rr = [
            r
            for r in rows
            if r["n"] == 4096
            and r["method"] == m
            and (m != "scaled" or r["delta"] == 0)
        ]
        axes[1].plot(
            [str(r["unit"]) for r in rr],
            [
                max(r["relative_std_error"] or 0, 1e-18)
                if r["std"] is not None
                else float("nan")
                for r in rr
            ],
            "o-",
            label=m,
        )
    axes[1].set(
        xlabel="Physical unit", ylabel="Relative SD error (floor1e-18)", yscale="log"
    )
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path / "scale_audit.png", dpi=150)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
