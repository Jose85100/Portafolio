"""Paired comparison: preserve raw decisions, sampling error and costs."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import time
import tracemalloc
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy

from src.baseline import ar_pvalue
from src.robust import robust_ar, sample

ROOT = Path(__file__).resolve().parents[1]


def run() -> None:
    cfg = json.loads((ROOT / "config.json").read_text())
    rows = []
    summary = []
    for scenario in cfg["scenarios"]:
        decisions = []
        start = time.perf_counter()
        tracemalloc.start()
        for rep in range(cfg["replications"]):
            seed = cfg["seed"] + rep
            y, x, z = sample(
                seed, scenario["n"], scenario["hetero"], cfg["c"], scenario["gamma"]
            )
            ps = [
                ar_pvalue(y, x, z, 1),
                robust_ar(y, x, z, 1, "HC1"),
                robust_ar(y, x, z, 1, "HC3"),
            ]
            ds = [int(p < cfg["alpha"]) for p in ps]
            decisions.append(ds)
            rows.append(
                {
                    "scenario": scenario["name"],
                    "seed": seed,
                    "p_F": ps[0],
                    "p_HC1": ps[1],
                    "p_HC3": ps[2],
                    "reject_F": ds[0],
                    "reject_HC1": ds[1],
                    "reject_HC3": ds[2],
                }
            )
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        d = np.array(decisions)
        rates = d.mean(axis=0)
        difference = d[:, 2] - d[:, 0]
        summary.append(
            {
                "scenario": scenario["name"],
                "rates": rates.tolist(),
                "mc_se": np.sqrt(rates * (1 - rates) / len(d)).tolist(),
                "hc3_minus_f": float(difference.mean()),
                "paired_se": float(difference.std(ddof=1) / np.sqrt(len(d))),
                "seconds": time.perf_counter() - start,
                "python_peak_bytes": peak,
            }
        )
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    with (out / "replications.csv").open("w") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    result = {
        "config": cfg,
        "summary": summary,
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "hardware": platform.platform(),
        "cpu": next(
            (
                line.split(":", 1)[1].strip()
                for line in Path("/proc/cpuinfo").read_text().splitlines()
                if line.startswith("model name")
            ),
            "unknown",
        )
        if Path("/proc/cpuinfo").exists()
        else platform.processor(),
        "data_sha256": hashlib.sha256(
            (out / "replications.csv").read_bytes()
        ).hexdigest(),
        "source_sha256": hashlib.sha256(
            (ROOT / "src/robust.py").read_bytes()
        ).hexdigest(),
        "timing_note": "Combined DGP and3 tests with tracemalloc; Python allocations, not RSS; no production cost claim.",
    }
    (out / "summary.json").write_text(json.dumps(result, indent=2))
    fig, ax = plt.subplots(figsize=(10, 5), layout="constrained")
    xp = np.arange(len(summary))
    for i, label, color in [
        (0, "F homocedástico", "#D55E00"),
        (1, "HC1 asintótico", "#009E73"),
        (2, "HC3 asintótico", "#0072B2"),
    ]:
        ax.bar(
            xp + (i - 1) * 0.25,
            [s["rates"][i] for s in summary],
            width=0.24,
            label=label,
            color=color,
        )
        ax.errorbar(
            xp + (i - 1) * 0.25,
            [s["rates"][i] for s in summary],
            yerr=[1.96 * s["mc_se"][i] for s in summary],
            fmt="none",
            color="black",
            capsize=2,
        )
    ax.axhline(0.05, color="black", ls="--", label="Nominal5%")
    ax.set_xticks(xp, [s["scenario"] for s in summary], rotation=12)
    ax.set_ylabel("Fracción de rechazos de β=1 (verdadero)")
    ax.set_title(
        "AR: robustez a heterocedasticidad y límite por exclusión\nSintético; ±1,96 errores estándar Monte Carlo"
    )
    ax.legend()
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(out / "comparison.png", dpi=150)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
