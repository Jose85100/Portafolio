"""18 deterministic population cases with an independent Schur-complement oracle."""

import csv
from collections.abc import Callable
import json
import platform
import time
import tracemalloc
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.joint_gate import correct_covariance_joint
from src.moments import Estimate, correct_covariance, population_covariance


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = json.loads((root / "config_joint.json").read_text())
    rows = []
    for beta in cfg["effects"]:
        s = population_covariance(beta)
        for variance in cfg["assumed_variances"]:
            old = correct_covariance(s, variance, cfg["condition_cap"])
            new = correct_covariance_joint(
                s, variance, cfg["condition_cap"], cfg["joint_psd_tolerance"]
            )
            latent = s.copy()
            latent[1, 1] -= variance
            residual = None
            if old.status == "accepted":
                # Independent oracle: PSD iff scalar residual >=0 given PD predictor block.
                residual = float(
                    latent[2, 2]
                    - latent[:2, 2] @ np.linalg.solve(latent[:2, :2], latent[:2, 2])
                )
                assert (new.status == "accepted") == (
                    residual >= -cfg["joint_psd_tolerance"]
                )
            methods: list[tuple[str, Callable[..., Estimate]]] = [
                ("regressor_only", correct_covariance),
                ("full_joint", correct_covariance_joint),
            ]
            for method, func in methods:
                times = []
                for _ in range(cfg["latency_repeats"]):
                    start = time.perf_counter()
                    func(s, variance, cfg["condition_cap"])
                    times.append(time.perf_counter() - start)
                tracemalloc.start()
                func(s, variance, cfg["condition_cap"])
                peak = tracemalloc.get_traced_memory()[1]
                tracemalloc.stop()
                rows.append(
                    {
                        "beta": beta,
                        "declared_variance": variance,
                        "method": method,
                        "status": old.status
                        if method == "regressor_only"
                        else new.status,
                        "slope": old.slope if method == "regressor_only" else new.slope,
                        "schur_residual_variance": residual,
                        "median_seconds": float(np.median(times)),
                        "peak_python_bytes": peak,
                    }
                )
    out = root / "results"
    with (out / "joint_cases.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    bad_old = sum(
        r["method"] == "regressor_only"
        and r["status"] == "accepted"
        and r["schur_residual_variance"] < -cfg["joint_psd_tolerance"]
        for r in rows
    )
    bad_new = sum(
        r["method"] == "full_joint"
        and r["status"] == "accepted"
        and r["schur_residual_variance"] < -cfg["joint_psd_tolerance"]
        for r in rows
    )
    assert bad_old == 4 and bad_new == 0
    for r in rows:
        if r["declared_variance"] == 1:
            assert r["status"] == "accepted" and abs(r["slope"] - r["beta"]) < 1e-10
    summary = {
        "config": cfg,
        "population_cases": len(rows) // 2,
        "method_rows": len(rows),
        "impossible_accepted_baseline": bad_old,
        "impossible_accepted_joint": bad_new,
        "true_variance_coefficients_preserved": True,
        "false_variance_0.5_passes_both": True,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "interpretation": "Necessary moment compatibility, not causal confidence or proof of external variance",
    }
    (out / "joint_summary.json").write_text(json.dumps(summary, indent=2))
    plt.rcParams.update(
        {
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.2,
        }
    )
    fig, ax = plt.subplots(figsize=(8, 4))
    group = [
        r
        for r in rows
        if r["beta"] == 0
        and r["method"] == "regressor_only"
        and r["schur_residual_variance"] is not None
    ]
    ax.plot(
        [r["declared_variance"] for r in group],
        [r["schur_residual_variance"] for r in group],
        "o-",
        color="#176D9C",
    )
    ax.axhline(
        0, color="black", ls="--", label="Varianza residual no negativa requerida"
    )
    bad = [r for r in group if r["schur_residual_variance"] < 0]
    ax.scatter(
        [r["declared_variance"] for r in bad],
        [r["schur_residual_variance"] for r in bad],
        color="#BC6536",
        marker="x",
        s=80,
        label="Aceptado por gate antiguo; rechazado por gate conjunto",
    )
    ax.set(
        xlabel="Varianza de error declarada",
        ylabel="Varianza residual latente de Y (Schur)",
        title="β=0: un bloque de regresores válido no basta",
    )
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "joint_audit.png", dpi=160)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
