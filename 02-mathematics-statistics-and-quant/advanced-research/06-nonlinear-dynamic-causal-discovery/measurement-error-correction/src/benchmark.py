"""Re-execute26October design; measure selection, bias and matched baselines."""

import csv
import json
import platform
import time
import tracemalloc
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.moments import estimate, generate


def save(path, rows):
    with path.open("w") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = json.loads((root / "config.json").read_text())
    assert cfg["true_noise_variance"] == 1.0
    rows = []
    for n in cfg["sample_sizes"]:
        for effect in cfg["effects"]:
            for rep in range(cfg["replicates"]):
                seed = cfg["seed"] + 1000 * n + 100 * int(effect * 100) + rep
                x, w, y, z = generate(n, effect, seed)
                naive = float(
                    np.linalg.lstsq(np.column_stack([np.ones(n), x, w]), y, rcond=None)[
                        0
                    ][1]
                )
                oracle = float(
                    np.linalg.lstsq(np.column_stack([np.ones(n), x, z]), y, rcond=None)[
                        0
                    ][1]
                )
                for assumed in cfg["assumed_noise_variances"]:
                    tracemalloc.start()
                    start = time.perf_counter()
                    r = estimate(x, w, y, assumed, cfg["max_condition"])
                    elapsed = time.perf_counter() - start
                    peak = tracemalloc.get_traced_memory()[1]
                    tracemalloc.stop()
                    rows.append(
                        {
                            "n": n,
                            "effect": effect,
                            "replicate": rep,
                            "seed": seed,
                            "assumed_variance": assumed,
                            "status": r.status,
                            "slope": r.slope,
                            "condition": r.condition,
                            "naive_slope": naive,
                            "oracle_observed_z_slope": oracle,
                            "seconds": elapsed,
                            "peak_python_bytes": peak,
                        }
                    )
    out = root / "results"
    save(out / "replicates.csv", rows)
    summary = []
    for n in cfg["sample_sizes"]:
        for effect in cfg["effects"]:
            for assumed in cfg["assumed_noise_variances"]:
                group = [
                    r
                    for r in rows
                    if r["n"] == n
                    and r["effect"] == effect
                    and r["assumed_variance"] == assumed
                ]
                valid = [r for r in group if r["status"] == "accepted"]
                errors = np.array([r["slope"] - effect for r in valid])
                baseline_errors = np.array([r["naive_slope"] - effect for r in valid])
                oracle_errors = np.array(
                    [r["oracle_observed_z_slope"] - effect for r in valid]
                )
                summary.append(
                    {
                        "n": n,
                        "effect": effect,
                        "assumed_variance": assumed,
                        "accepted": len(valid),
                        "replicates": len(group),
                        "acceptance": len(valid) / len(group),
                        "bias_accepted": float(errors.mean()) if len(valid) else None,
                        "rmse_accepted": float(np.sqrt(np.mean(errors**2)))
                        if len(valid)
                        else None,
                        "naive_rmse_matched": float(
                            np.sqrt(np.mean(baseline_errors**2))
                        )
                        if len(valid)
                        else None,
                        "oracle_rmse_matched": float(np.sqrt(np.mean(oracle_errors**2)))
                        if len(valid)
                        else None,
                        "median_seconds": float(
                            np.median([r["seconds"] for r in group])
                        ),
                        "max_python_bytes": max(r["peak_python_bytes"] for r in group),
                    }
                )
    save(out / "summary.csv", summary)
    selected = [r for r in summary if r["n"] == 2000 and r["assumed_variance"] == 1]
    threshold = cfg["hypothesis"]
    checks = {
        "bias": all(
            abs(r["bias_accepted"]) <= threshold["known_variance_abs_bias_n2000_max"]
            for r in selected
        ),
        "acceptance": all(
            r["acceptance"] >= threshold["known_variance_acceptance_n2000_min"]
            for r in selected
        ),
        "matched_rmse": all(
            r["rmse_accepted"] / r["naive_rmse_matched"]
            <= threshold["known_variance_rmse_vs_proxy_n2000_max_ratio"]
            for r in selected
        ),
    }
    assert all(checks.values()), checks
    result = {
        "research_date": "2026-10-26",
        "recovery_execution_date": "2026-10-27",
        "provenance": "Source reconstructed from visible session history after scratch worktree loss; outputs regenerated, not restored byte-for-byte",
        "config": cfg,
        "datasets": len(rows) // 4,
        "estimator_runs": len(rows),
        "checks": checks,
        "n2000": [r for r in summary if r["n"] == 2000],
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "selection_warning": "All error comparisons conditional on correction acceptance on same replicates; abstention cost not assigned",
    }
    (out / "summary.json").write_text(json.dumps(result, indent=2))
    plt.rcParams.update(
        {
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.2,
            "font.size": 10,
        }
    )
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for assumed, color, label in [
        (0.0, "#BC6536", "OLS proxy"),
        (0.5, "#8B6BAE", "Varianza declarada0.5"),
        (1.0, "#176D9C", "Varianza correcta1.0"),
    ]:
        g = [
            r for r in summary if r["effect"] == 0 and r["assumed_variance"] == assumed
        ]
        axes[0].plot(
            [r["n"] for r in g],
            [r["rmse_accepted"] for r in g],
            "o-",
            label=label,
            color=color,
        )
    axes[0].set(
        xlabel="Observaciones por réplica",
        ylabel="RMSE condicionado a aceptación",
        title="β=0: información externa y error de muestra",
    )
    axes[0].legend(fontsize=8)
    for assumed, color in [
        (0.0, "#BC6536"),
        (0.5, "#8B6BAE"),
        (1.0, "#176D9C"),
        (1.5, "#5A8850"),
    ]:
        g = [
            r for r in summary if r["effect"] == 0 and r["assumed_variance"] == assumed
        ]
        axes[1].plot(
            [r["n"] for r in g],
            [r["acceptance"] for r in g],
            "o-",
            color=color,
            label=f"Varianza declarada {assumed}",
        )
    axes[1].set(
        xlabel="Observaciones por réplica",
        ylabel="Fracción de200 réplicas aceptadas",
        ylim=(-0.02, 1.05),
        title="Abstención por momentos incompatibles",
    )
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "audit.png", dpi=160)
    plt.close(fig)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
