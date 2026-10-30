"""Calendar sensitivity, identical hazards and horizon in both comparators."""

import csv
import json
import time
import tracemalloc
from dataclasses import asdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.calendar import project_calendar

ROOT = Path(__file__).resolve().parents[1]


def run():
    cfg = json.loads((ROOT / "benchmarks/calendar_config.json").read_text())
    rows = []
    tracemalloc.start()
    start = time.perf_counter()
    for rho in cfg["discount_forces"]:
        for n in cfg["partitions"]:
            r = project_calendar(
                [cfg["horizon_years"] / n] * n,
                [cfg["default_hazard"]] * n,
                [cfg["prepay_hazard"]] * n,
                [cfg["ead"]] * n,
                lgd=cfg["lgd"],
                discount_force=rho,
            )
            rows.append(
                dict(
                    discount_force=rho,
                    intervals=n,
                    relative_endpoint_bias=r.endpoint_loss / r.exact_loss - 1,
                    **asdict(r),
                )
            )
    meta = {
        "config": cfg,
        "seconds": time.perf_counter() - start,
        "peak_bytes": tracemalloc.get_traced_memory()[1],
        "hypothesis": abs(rows[0]["relative_endpoint_bias"]) > 0.02,
    }
    tracemalloc.stop()
    with (ROOT / "results/calendar.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (ROOT / "results/calendar_metrics.json").write_text(json.dumps(meta, indent=2))
    fig, ax = plt.subplots(figsize=(7, 4))
    for rho in cfg["discount_forces"]:
        rr = [r for r in rows if r["discount_force"] == rho]
        ax.plot(
            [r["intervals"] for r in rr],
            [-100 * r["relative_endpoint_bias"] for r in rr],
            marker="o",
            label=f"descuento continuo {rho}/año",
        )
    ax.set(
        xscale="log",
        xlabel="Intervalos por año (misma intensidad anual)",
        ylabel="Subestimación por descuento al cierre (%)",
        title="Integrar tiempo de default elimina sesgo de calendario",
    )
    ax.legend()
    fig.tight_layout()
    fig.savefig(ROOT / "results/calendar.png", dpi=150)
    plt.close(fig)
    print(json.dumps(meta, indent=2))
    print(rows)


if __name__ == "__main__":
    run()
