"""Small deterministic probability-flow audit with a rational arithmetic oracle."""

import csv
import json
import platform
import sys
import time
import tracemalloc
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.model import project

ROOT = Path(__file__).resolve().parents[1]


def save(path, rows):
    with path.open("w") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def run() -> None:
    cfg = json.loads((ROOT / "benchmarks/config.json").read_text())
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    n = cfg["periods"]
    d = cfg["conditional_default"]
    pp = cfg["conditional_prepayment"]
    e = cfg["conditional_ead"]
    lgd = cfg["lgd"]
    r = cfg["period_discount_rate"]
    start = time.perf_counter()
    tracemalloc.start()
    baseline = project([d] * n, [0.0] * n, [e] * n, lgd, r)
    joint = project([d] * n, [pp] * n, [e] * n, lgd, r)
    rows = []
    for p in cfg["prepayment_grid"]:
        result = project([d] * n, [p] * n, [e] * n, lgd, r)
        rows.append(
            {
                "conditional_prepayment": p,
                "default_probability": result.default_probability,
                "prepayment_probability": result.prepayment_probability,
                "active_probability": result.active_probability,
                "expected_loss": result.expected_loss,
                "mass_error": result.maximum_mass_error,
            }
        )
    active = Fraction(1)
    oracle = Fraction(0)
    for t in range(1, n + 1):
        oracle += (
            active
            * Fraction(str(d))
            * Fraction(str(e))
            * Fraction(str(lgd))
            / (1 + Fraction(str(r))) ** t
        )
        active *= 1 - Fraction(str(d)) - Fraction(str(pp))
    seconds = time.perf_counter() - start
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    save(out / "sensitivity.csv", rows)
    save(out / "joint_periods.csv", [asdict(x) for x in joint.periods])
    save(out / "baseline_periods.csv", [asdict(x) for x in baseline.periods])
    overstated = baseline.expected_loss / joint.expected_loss - 1
    meta = {
        "config": cfg,
        "baseline_expected_loss": baseline.expected_loss,
        "joint_expected_loss": joint.expected_loss,
        "baseline_default_probability": baseline.default_probability,
        "joint_default_probability": joint.default_probability,
        "relative_baseline_overstatement": overstated,
        "rational_oracle_loss": float(oracle),
        "rational_oracle_error": abs(joint.expected_loss - float(oracle)),
        "hypothesis_passed": overstated >= 0.2,
        "seconds": seconds,
        "peak_tracemalloc_bytes": peak,
        "python": sys.version,
        "platform": platform.platform(),
        "logical_cpus": __import__("os").cpu_count(),
    }
    (out / "metrics.json").write_text(json.dumps(meta, indent=2))
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    axes[0].bar(
        ["Sin prepago", "Salidas conjuntas"],
        [baseline.expected_loss, joint.expected_loss],
        color=["#C77432", "#3567A8"],
    )
    axes[0].set(
        ylabel="Pérdida esperada descontada (unidades)",
        title="Misma PD/EAD/LGD; distinto universo activo",
    )
    axes[1].plot(
        [x["conditional_prepayment"] for x in rows],
        [x["default_probability"] for x in rows],
        marker="o",
        color="#3567A8",
    )
    axes[1].set(
        xlabel="Probabilidad de prepago por período | activo",
        ylabel="Incidencia acumulada de default a12períodos",
        title="PD condicional fija; el prepago compite",
    )
    fig.tight_layout()
    fig.savefig(out / "audit.png", dpi=150)
    plt.close(fig)
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    run()
