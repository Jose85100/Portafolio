"""Independent replicated Gaussian experiments: prediction is not intervention."""

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
from scipy.stats import beta as beta_distribution

from src.confounding import generate, lag_test, paired_intervention


def save(path, rows):
    with path.open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = json.loads((root / "config.json").read_text())
    out = root / "results"
    assert (
        cfg["loading_x"],
        cfg["loading_y"],
        cfg["noise_x_sd"],
        cfg["noise_y_sd"],
    ) == (0.8, 0.8, 0.5, 0.5), "Fixed audited DGP constants changed"
    rows = []
    for n in cfg["sample_sizes"]:
        for effect in cfg["effects"]:
            for rep in range(cfg["replicates"]):
                seed = cfg["seed"] + n * 1000 + int(effect * 100) * 100 + rep
                sample = generate(n, effect, seed, cfg["proxy_noise_sd"])
                for method, control in [
                    ("omitted", None),
                    ("observed_correct_lag", sample.z_lag2),
                    ("observed_wrong_lag", sample.z_wrong_lag),
                    ("noisy_proxy", sample.z_proxy),
                ]:
                    tracemalloc.start()
                    start = time.perf_counter()
                    result = lag_test(sample.y, sample.x_lag, control, cfg["alpha"])
                    elapsed = time.perf_counter() - start
                    peak = tracemalloc.get_traced_memory()[1]
                    tracemalloc.stop()
                    rows.append(
                        {
                            "n": n,
                            "effect": effect,
                            "replicate": rep,
                            "seed": seed,
                            "method": method,
                            "slope": result.slope,
                            "p_value": result.p_value,
                            "f_statistic": result.f_statistic,
                            "reject": int(result.p_value < cfg["alpha"]),
                            "ci_covers_structural_effect": int(
                                result.ci_low <= effect <= result.ci_high
                            ),
                            "slope_bias_vs_structural": result.slope - effect,
                            "paired_intervention_mean": float(
                                np.mean(paired_intervention(sample, 1) - sample.y)
                            ),
                            "seconds": elapsed,
                            "peak_python_bytes": peak,
                        }
                    )
    save(out / "replicates.csv", rows)
    aggregate = []
    for n in cfg["sample_sizes"]:
        for effect in cfg["effects"]:
            for method in [
                "omitted",
                "observed_correct_lag",
                "observed_wrong_lag",
                "noisy_proxy",
            ]:
                group = [
                    r
                    for r in rows
                    if r["n"] == n and r["effect"] == effect and r["method"] == method
                ]
                k = sum(r["reject"] for r in group)
                m = len(group)
                lo = 0 if k == 0 else float(beta_distribution.ppf(0.025, k, m - k + 1))
                hi = 1 if k == m else float(beta_distribution.ppf(0.975, k + 1, m - k))
                aggregate.append(
                    {
                        "n": n,
                        "effect": effect,
                        "method": method,
                        "replicates": m,
                        "rejection_rate": k / m,
                        "mc_95_low": lo,
                        "mc_95_high": hi,
                        "mean_slope": float(np.mean([r["slope"] for r in group])),
                        "mean_bias_vs_structural": float(
                            np.mean([r["slope_bias_vs_structural"] for r in group])
                        ),
                        "structural_ci_coverage": float(
                            np.mean([r["ci_covers_structural_effect"] for r in group])
                        ),
                        "median_seconds": float(
                            np.median([r["seconds"] for r in group])
                        ),
                        "max_python_bytes": max(r["peak_python_bytes"] for r in group),
                    }
                )
    save(out / "summary.csv", aggregate)
    controlled = [r for r in aggregate if r["method"] == "observed_correct_lag"]
    checks = {
        "null_rejection_at_most_threshold": all(
            r["rejection_rate"] <= cfg["thresholds"]["controlled_null_rejection_max"]
            for r in controlled
            if r["effect"] == 0
        ),
        "power_at_least_threshold_n500plus": all(
            r["rejection_rate"] >= cfg["thresholds"]["controlled_power_min_at_n500"]
            for r in controlled
            if r["effect"] > 0 and r["n"] >= 500
        ),
        "bias_at_n2000_below_threshold": all(
            abs(r["mean_bias_vs_structural"])
            <= cfg["thresholds"]["controlled_bias_abs_max_at_n2000"]
            for r in controlled
            if r["n"] == 2000
        ),
    }
    assert all(checks.values()), checks
    summary = {
        "config": cfg,
        "regression_fits": len(rows),
        "independent_datasets": len(rows) // 4,
        "checks": checks,
        "omitted_population_slope_bias": 0.64 / 0.89,
        "proxy_population_slope_bias": 0.32 / 0.57,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "hardware": platform.machine(),
        "selected_n500": [r for r in aggregate if r["n"] == 500],
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
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
    styles = [
        ("omitted", "#BC6536", "omitido"),
        ("observed_correct_lag", "#176D9C", "control correcto"),
        ("observed_wrong_lag", "#8B6BAE", "lag incorrecto"),
        ("noisy_proxy", "#5A8850", "proxy ruidoso"),
    ]
    for method, color, label in styles:
        null = [r for r in aggregate if r["method"] == method and r["effect"] == 0]
        axes[0].plot(
            [r["n"] for r in null],
            [r["rejection_rate"] for r in null],
            "o-",
            label=label,
            color=color,
        )
        axes[1].plot(
            [r["n"] for r in null],
            [r["mean_bias_vs_structural"] for r in null],
            "o-",
            label=label,
            color=color,
        )
    axes[0].axhline(0.05, ls="--", color="black", lw=1, label="α=5% (control correcto)")
    axes[0].set(
        xlabel="Observaciones por réplica",
        ylabel="Fracción de rechazos predictivos",
        title="Efecto estructural cero: no confundir causalidad",
        ylim=(-0.03, 1.05),
    )
    axes[0].legend(fontsize=8)
    axes[1].axhline(0, ls="--", color="black", lw=1)
    axes[1].set(
        xlabel="Observaciones por réplica",
        ylabel="Sesgo frente al efecto estructural β=0",
        title="Más datos no elimina confusión omitida",
    )
    fig.tight_layout()
    fig.savefig(out / "audit.png", dpi=160)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
