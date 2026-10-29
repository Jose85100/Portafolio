"""54 tiny exact-expectation scenarios; no Monte Carlo, empirical or timing claims."""

from __future__ import annotations
import csv
import hashlib
import json
import platform
import time
import tracemalloc
from pathlib import Path
from typing import Any
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from src.monetary import policies, loss, oracle, best_response

ROOT = Path(__file__).resolve().parents[1]


def run() -> None:
    cfg = json.loads((ROOT / "config.json").read_text())
    rows: list[dict[str, Any]] = []
    states = []
    start = time.perf_counter()
    tracemalloc.start()
    for alpha in cfg["alpha_values"]:
        for weight in cfg["weight_values"]:
            for target in cfg["target_values"]:
                for scale in cfg["shock_scales"]:
                    by_regime: dict[str, list[tuple[float, float, float, float]]] = {}
                    max_oracle_error = 0.0
                    for shock in [-scale, scale]:
                        for name, (pi, expected) in policies(
                            shock, alpha, weight, target
                        ).items():
                            L = loss(pi, expected, shock, alpha, weight, target)
                            output = alpha * (pi - expected) + shock
                            by_regime.setdefault(name, []).append(
                                (pi, expected, L, output)
                            )
                            states.append(
                                {
                                    "alpha": alpha,
                                    "weight": weight,
                                    "target": target,
                                    "shock_scale": scale,
                                    "shock": shock,
                                    "regime": name,
                                    "pi": pi,
                                    "expected_pi": expected,
                                    "loss": L,
                                    "output": output,
                                    "state_probability": 0.5,
                                }
                            )
                        expected = weight * alpha * target
                        max_oracle_error = max(
                            max_oracle_error,
                            abs(
                                oracle(expected, shock, alpha, weight, target)
                                - best_response(expected, shock, alpha, weight, target)
                            ),
                        )
                    metrics = {
                        name: {
                            "loss": float(np.mean([v[2] for v in values])),
                            "mean_pi": float(np.mean([v[0] for v in values])),
                            "mean_output": float(np.mean([v[3] for v in values])),
                            "re_residual": abs(
                                float(np.mean([v[0] for v in values])) - values[0][1]
                            ),
                        }
                        for name, values in by_regime.items()
                    }
                    rows.append(
                        {
                            "alpha": alpha,
                            "weight": weight,
                            "target": target,
                            "shock_scale": scale,
                            "commitment_loss": metrics["commitment"]["loss"],
                            "discretion_loss": metrics["discretion"]["loss"],
                            "naive_loss_inconsistent": metrics[
                                "naive_fixed_expectations"
                            ]["loss"],
                            "commitment_re_residual": metrics["commitment"][
                                "re_residual"
                            ],
                            "discretion_re_residual": metrics["discretion"][
                                "re_residual"
                            ],
                            "naive_re_residual": metrics["naive_fixed_expectations"][
                                "re_residual"
                            ],
                            "commitment_mean_output": metrics["commitment"][
                                "mean_output"
                            ],
                            "discretion_mean_output": metrics["discretion"][
                                "mean_output"
                            ],
                            "naive_mean_output": metrics["naive_fixed_expectations"][
                                "mean_output"
                            ],
                            "loss_gap_identity_error": abs(
                                metrics["discretion"]["loss"]
                                - metrics["commitment"]["loss"]
                                - 0.5 * (weight * alpha * target) ** 2
                            ),
                            "max_best_response_oracle_error": max_oracle_error,
                        }
                    )
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed = time.perf_counter() - start
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    for path, data in [("cases.csv", rows), ("states.csv", states)]:
        with (out / path).open("w") as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)
    anchor = next(r for r in rows if all(r[k] == v for k, v in cfg["anchor"].items()))
    payload = {
        "config": cfg,
        "case_count": len(rows),
        "state_regime_records": len(states),
        "anchor": anchor,
        "max_loss_gap_identity_error": max(r["loss_gap_identity_error"] for r in rows),
        "max_best_response_oracle_error": max(
            r["max_best_response_oracle_error"] for r in rows
        ),
        "seconds": elapsed,
        "python_peak_bytes": peak,
        "hardware": platform.platform(),
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "source_sha256": hashlib.sha256(
            (ROOT / "src/monetary.py").read_bytes()
        ).hexdigest(),
        "data_sha256": hashlib.sha256((out / "cases.csv").read_bytes()).hexdigest(),
        "note": "Exact equiprobable ±sigma states; sigma0 repeats same zero state with probability0.5 each. No sampled uncertainty. Whole experiment instrumented Python allocation peak, not RSS or per-regime runtime.",
    }
    (out / "summary.json").write_text(json.dumps(payload, indent=2))
    selected = [
        r
        for r in rows
        if r["alpha"] == 1 and r["weight"] == 1 and r["shock_scale"] == 1
    ]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), layout="constrained")
    targets = [r["target"] for r in selected]
    for key, label, color, style in [
        ("commitment_loss", "Commitment", "#0072B2", "-o"),
        ("discretion_loss", "Discretion (RE)", "#D55E00", "-s"),
        ("naive_loss_inconsistent", "Naive (RE fails)", "#777777", "--x"),
    ]:
        axes[0].plot(
            targets, [r[key] for r in selected], style, label=label, color=color
        )
    axes[0].set_ylabel("Expected quadratic loss (normalized)")
    axes[0].legend(fontsize=8)
    axes[1].plot(
        targets,
        [r["naive_re_residual"] for r in selected],
        "-x",
        color="#777777",
        label="Naive RE residual",
    )
    axes[1].axhline(0, color="#0072B2", label="Commitment/discretion residual")
    axes[1].set_ylabel("|E inflation - expected inflation|")
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.set_xlabel("Output target above natural level k")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=0.2)
    fig.suptitle(
        "Inflation bias: low objective value is not an equilibrium certificate | synthetic"
    )
    fig.savefig(out / "comparison.png", dpi=150)
    plt.close(fig)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    run()
