"""Reproducible benchmark and raw artifacts for the gauge certificate."""

from __future__ import annotations

import csv
import json
import platform
import time
import tracemalloc
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

import matplotlib.pyplot as plt
import numpy as np

from .gauge import (
    analytic_jacobian,
    best_rank_one,
    canonicalize,
    finite_difference_jacobian,
    fisher_information,
    gauge_tangent,
    mean_matrix,
    spectral_certificate,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmarks"


def _timed_peak(function: Callable[[], np.ndarray]) -> tuple[np.ndarray, float, int]:
    tracemalloc.start()
    start = time.perf_counter_ns()
    result = function()
    elapsed = (time.perf_counter_ns() - start) / 1e6
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, elapsed, peak


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[int, int, float], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["m"]), int(row["n"]), float(row["noise_std"]))].append(row)
    summary: list[dict[str, Any]] = []
    for (m, n, noise), values in sorted(grouped.items()):
        summary.append(
            {
                "m": m,
                "n": n,
                "noise_std": noise,
                "replicates": len(values),
                "nullity_mode": int(round(float(np.median([x["nullity"] for x in values])))),
                "max_gauge_residual": max(float(x["gauge_residual"]) for x in values),
                "max_prediction_change": max(float(x["prediction_change"]) for x in values),
                "mean_jacobian_relative_error": float(
                    np.mean([x["jacobian_relative_error"] for x in values])
                ),
                "median_analytic_ms": float(np.median([x["analytic_ms"] for x in values])),
                "median_finite_difference_ms": float(np.median([x["finite_difference_ms"] for x in values])),
                "median_speedup": float(
                    np.median([float(x["finite_difference_ms"]) / float(x["analytic_ms"]) for x in values])
                ),
                "median_analytic_peak_bytes": float(np.median([x["analytic_peak_bytes"] for x in values])),
                "median_finite_difference_peak_bytes": float(
                    np.median([x["finite_difference_peak_bytes"] for x in values])
                ),
                "raw_log_norm_ratio_range": float(np.median([x["raw_spread"] for x in values])),
                "fixed_log_norm_ratio_range": float(np.median([x["fixed_spread"] for x in values])),
                "instability_reduction": float(np.median([x["instability_reduction"] for x in values])),
                "median_identifiable_condition": float(
                    np.median([x["condition_identifiable"] for x in values])
                ),
            }
        )
    return summary


def _plot(summary: list[dict[str, Any]], diagnostic: dict[str, Any]) -> None:
    selected = [row for row in summary if float(row["noise_std"]) == 0.05]
    labels = [f"{row['m']}×{row['n']}" for row in selected]
    colors = {"analytic": "#2457A6", "baseline": "#D58A22", "fixed": "#557A46"}
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 4.4))

    x = np.arange(len(selected))
    axes[0].plot(
        x, [row["median_analytic_ms"] for row in selected], "o-", color=colors["analytic"], label="Analítico"
    )
    axes[0].plot(
        x,
        [row["median_finite_difference_ms"] for row in selected],
        "s--",
        color=colors["baseline"],
        label="Dif. finitas",
    )
    axes[0].set_yscale("log")
    axes[0].set_xticks(x, labels)
    axes[0].set_ylabel("Tiempo mediano (ms, escala log)")
    axes[0].set_title("Costo del Jacobiano")
    axes[0].legend(frameon=False)

    axes[1].bar(
        x,
        [row["raw_log_norm_ratio_range"] for row in selected],
        0.46,
        color=colors["baseline"],
        label="Sin fijar",
    )
    axes[1].scatter(
        x,
        [row["fixed_log_norm_ratio_range"] for row in selected],
        s=55,
        marker="D",
        facecolors="white",
        edgecolors=colors["fixed"],
        linewidths=1.8,
        zorder=3,
        label="Gauge fijo",
    )
    axes[1].set_xticks(x, labels)
    axes[1].set_ylabel("Rango de log(||u||/||v||)")
    axes[1].set_title("Inestabilidad paramétrica")
    axes[1].legend(frameon=False)

    axes[2].bar(
        ["Regular", "u=0"],
        [diagnostic["regular_nullity"], diagnostic["degenerate_nullity"]],
        color=[colors["analytic"], colors["baseline"]],
    )
    axes[2].axhline(1, color="#333333", linestyle="--", linewidth=1)
    axes[2].text(0.03, 1.03, "esperado: 1", color="#333333", fontsize=9)
    axes[2].set_ylabel("Nulidad numérica de Fisher")
    axes[2].set_title("Caso negativo: singularidad extra")

    for axis in axes:
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(axis="y", color="#D9D9D9", linewidth=0.6, alpha=0.7)
    fig.suptitle("Certificado gauge rango uno — 20 réplicas por configuración", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "gauge-certificate.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)
    raw: list[dict[str, Any]] = []
    scales = np.asarray(config["gauge_scales"], dtype=np.float64)
    for shape_index, (m, n) in enumerate(config["shapes"]):
        for noise_index, noise_std in enumerate(config["noise_std"]):
            for replicate in range(config["replicates"]):
                seed = int(config["seed"] + 100_000 * shape_index + 10_000 * noise_index + replicate)
                rng = np.random.default_rng(seed)
                true_u = rng.normal(size=m)
                true_v = rng.normal(size=n)
                true_u /= np.linalg.norm(true_u)
                true_v /= np.linalg.norm(true_v)
                data = mean_matrix(true_u, true_v) + float(noise_std) * rng.normal(size=(m, n))
                fitted_u, fitted_v = best_rank_one(data)

                analytic, analytic_ms, analytic_peak = _timed_peak(
                    lambda: analytic_jacobian(fitted_u, fitted_v)
                )
                finite, finite_ms, finite_peak = _timed_peak(
                    lambda: finite_difference_jacobian(
                        fitted_u, fitted_v, float(config["finite_difference_step"])
                    )
                )
                certificate = spectral_certificate(fisher_information(analytic, float(noise_std)))
                tangent = gauge_tangent(fitted_u, fitted_v)
                residual = float(np.linalg.norm(analytic @ tangent) / np.linalg.norm(tangent))

                raw_ratios: list[float] = []
                fixed_ratios: list[float] = []
                prediction_changes: list[float] = []
                base_prediction = mean_matrix(fitted_u, fitted_v)
                for scale in scales:
                    scaled_u, scaled_v = scale * fitted_u, fitted_v / scale
                    fixed_u, fixed_v = canonicalize(scaled_u, scaled_v)
                    raw_ratios.append(float(np.log(np.linalg.norm(scaled_u) / np.linalg.norm(scaled_v))))
                    fixed_ratios.append(float(np.log(np.linalg.norm(fixed_u) / np.linalg.norm(fixed_v))))
                    prediction_changes.append(
                        float(np.linalg.norm(mean_matrix(fixed_u, fixed_v) - base_prediction))
                    )
                raw_spread = float(np.ptp(raw_ratios))
                fixed_spread = float(np.ptp(fixed_ratios))
                raw.append(
                    {
                        "seed": seed,
                        "m": m,
                        "n": n,
                        "noise_std": noise_std,
                        "replicate": replicate,
                        "nullity": certificate.nullity,
                        "rank": certificate.rank,
                        "condition_identifiable": certificate.condition_identifiable,
                        "gauge_residual": residual,
                        "jacobian_relative_error": float(
                            np.linalg.norm(analytic - finite) / np.linalg.norm(analytic)
                        ),
                        "analytic_ms": analytic_ms,
                        "finite_difference_ms": finite_ms,
                        "analytic_peak_bytes": analytic_peak,
                        "finite_difference_peak_bytes": finite_peak,
                        "raw_spread": raw_spread,
                        "fixed_spread": fixed_spread,
                        "instability_reduction": 1.0 - fixed_spread / raw_spread,
                        "prediction_change": max(prediction_changes),
                        "reconstruction_rmse": float(np.sqrt(np.mean((data - base_prediction) ** 2))),
                    }
                )

    summary = _summarize(raw)
    regular_u = np.array([1.0, -0.5, 0.25])
    regular_v = np.array([0.8, -0.3])
    regular = spectral_certificate(fisher_information(analytic_jacobian(regular_u, regular_v), 0.05))
    degenerate = spectral_certificate(fisher_information(analytic_jacobian(np.zeros(3), regular_v), 0.05))
    diagnostic = {
        "regular_nullity": regular.nullity,
        "degenerate_nullity": degenerate.nullity,
        "interpretation": "nullity greater than one is not certified as scale-only gauge",
    }
    _write_csv(OUT / "raw.csv", raw)
    _write_csv(OUT / "summary.csv", summary)
    gates = config["success"]
    results: dict[str, Any] = {
        "design": {"rows": len(raw), "decisions": len(raw) * 3, "seed": config["seed"]},
        "diagnostic": diagnostic,
        "global": {
            "max_gauge_residual": max(row["gauge_residual"] for row in raw),
            "max_prediction_change": max(row["prediction_change"] for row in raw),
            "min_instability_reduction": min(row["instability_reduction"] for row in raw),
            "max_jacobian_relative_error": max(row["jacobian_relative_error"] for row in raw),
            "min_speedup": min(row["finite_difference_ms"] / row["analytic_ms"] for row in raw),
        },
        "gates": {
            "gauge_residual": max(row["gauge_residual"] for row in raw) <= gates["max_gauge_residual"],
            "prediction_invariance": max(row["prediction_change"] for row in raw)
            <= gates["max_prediction_change"],
            "instability_reduction": min(row["instability_reduction"] for row in raw)
            >= gates["min_instability_reduction"],
            "regular_nullity_exactly_one": regular.nullity == 1,
            "degenerate_case_rejected": degenerate.nullity > 1,
        },
        "summary": summary,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
    }
    (OUT / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    _plot(summary, diagnostic)
    print(json.dumps(results["global"], indent=2))
    if not all(results["gates"].values()):
        raise SystemExit("At least one predeclared success gate failed")


if __name__ == "__main__":
    main()
