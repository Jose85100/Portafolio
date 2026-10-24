"""Paired synthetic Monte Carlo with complete decision ledger and timing."""

from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
import platform
import time
import tracemalloc
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from src.inference import ar_pvalue, first_stage_f, sample, wald_pvalue

ROOT = Path(__file__).resolve().parents[1]


def run() -> dict[str, object]:
    config = json.loads((ROOT / "config.json").read_text())
    rows = []
    summaries = []
    for scenario in config["scenarios"]:
        start = time.perf_counter()
        tracemalloc.start()
        pairs = []
        fs = []
        for rep in range(config["replications"]):
            seed = config["seed"] + rep
            y, x, z = sample(
                seed,
                config["n"],
                scenario["strength"],
                config["rho"],
                scenario["exclusion"],
            )
            ar = ar_pvalue(y, x, z, config["beta_null"])
            wald = wald_pvalue(y, x, z, config["beta_null"])
            first_f = first_stage_f(x, z)
            a, w = int(ar < config["alpha"]), int(wald < config["alpha"])
            pairs.append((a, w))
            fs.append(first_f)
            rows.append(
                dict(
                    scenario=scenario["name"],
                    replication=rep,
                    seed=seed,
                    ar_pvalue=ar,
                    wald_pvalue=wald,
                    first_stage_f=first_f,
                    ar_reject=a,
                    wald_reject=w,
                )
            )
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        values = np.array(pairs)
        a_rate, w_rate = values.mean(axis=0)
        diff = values[:, 0] - values[:, 1]
        summaries.append(
            dict(
                scenario=scenario["name"],
                ar_rejection=float(a_rate),
                wald_rejection=float(w_rate),
                ar_mc_se=float(np.sqrt(a_rate * (1 - a_rate) / len(values))),
                wald_mc_se=float(np.sqrt(w_rate * (1 - w_rate) / len(values))),
                paired_difference_se=float(diff.std(ddof=1) / np.sqrt(len(values))),
                median_first_stage_f=float(np.median(fs)),
                elapsed_seconds=time.perf_counter() - start,
                python_peak_bytes=peak,
            )
        )
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    with (output / "replications.csv").open("w") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    metadata = dict(
        config=config,
        summaries=summaries,
        python=platform.python_version(),
        numpy=np.__version__,
        scipy=scipy.__version__,
        matplotlib=matplotlib.__version__,
        platform=platform.platform(),
        cpu=platform.processor(),
        source_sha256=hashlib.sha256(
            (ROOT / "src/inference.py").read_bytes()
        ).hexdigest(),
        data_sha256=hashlib.sha256(
            (output / "replications.csv").read_bytes()
        ).hexdigest(),
        timing_note="Combined generation and both methods, instrumented with tracemalloc; Python allocation peak, not RSS.",
    )
    (output / "summary.json").write_text(json.dumps(metadata, indent=2))
    fig, ax = plt.subplots(figsize=(9, 4.5), layout="constrained")
    xp = np.arange(len(summaries))
    for delta, key, se_key, color, label in [
        (-0.18, "wald_rejection", "wald_mc_se", "#D55E00", "Wald convencional"),
        (0.18, "ar_rejection", "ar_mc_se", "#0072B2", "Anderson–Rubin"),
    ]:
        ax.bar(
            xp + delta,
            [s[key] for s in summaries],
            width=0.35,
            color=color,
            label=label,
        )
        ax.errorbar(
            xp + delta,
            [s[key] for s in summaries],
            yerr=[1.96 * s[se_key] for s in summaries],
            fmt="none",
            color="#333333",
            capsize=3,
        )
    ax.axhline(0.05, color="black", linestyle="--", label="Nivel nominal 5%")
    ax.set_xticks(xp, [s["scenario"] for s in summaries])
    ax.set_ylabel("Fracción de rechazos (nula verdadera β=1)")
    ax.set_title(
        "Inferencia IV: relevancia débil y falsación de exclusión\nDatos sintéticos; barras ±1,96 SE Monte Carlo"
    )
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper left")
    fig.savefig(output / "rejection_rates.png", dpi=160)
    plt.close(fig)
    print(json.dumps(summaries, indent=2))
    return metadata


if __name__ == "__main__":
    run()
