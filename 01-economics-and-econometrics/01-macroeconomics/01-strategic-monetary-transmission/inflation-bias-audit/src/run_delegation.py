"""Reproducible exact-state experiment; no empirical inference."""

from pathlib import Path
import csv
import hashlib
import json
import platform
import time
import tracemalloc
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .delegation import optimal_weight, oracle_weight, social_loss, state_average


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = json.loads((root / "delegation-config.json").read_text())
    out = root / "results"
    start = time.perf_counter()
    tracemalloc.start()
    rows = []
    for a in cfg["alpha"]:
        for w in cfg["social_weight"]:
            for k in cfg["target"]:
                for s in cfg["sigma"]:
                    q = optimal_weight(a, w, k, s)
                    val = social_loss(q, a, w, k, s)
                    oracle = oracle_weight(a, w, k, s)
                    rows.append(
                        dict(
                            alpha=a,
                            weight=w,
                            target=k,
                            sigma=s,
                            q=q,
                            baseline=social_loss(w, a, w, k, s),
                            optimal=val,
                            zero_weight=social_loss(0, a, w, k, s),
                            oracle_loss_error=abs(
                                val - social_loss(oracle, a, w, k, s)
                            ),
                            state_error=abs(val - state_average(q, a, w, k, s)),
                        )
                    )
    seconds = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    with (out / "delegation.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    anchor = next(
        r
        for r in rows
        if all(r[z] == 1 for z in ["alpha", "weight", "target", "sigma"])
    )
    summary = dict(
        cases=len(rows),
        anchor=anchor,
        max_oracle_loss_error=max(r["oracle_loss_error"] for r in rows),
        max_state_error=max(r["state_error"] for r in rows),
        seconds=seconds,
        python_peak_bytes=peak,
        platform=platform.platform(),
        python=platform.python_version(),
        data_sha256=hashlib.sha256((out / "delegation.csv").read_bytes()).hexdigest(),
        source_sha256=hashlib.sha256(
            (root / "src/delegation.py").read_bytes()
        ).hexdigest(),
        config=cfg,
    )
    assert summary["max_oracle_loss_error"] < 1e-10
    assert summary["max_state_error"] < 1e-10
    (out / "delegation-summary.json").write_text(json.dumps(summary, indent=2))
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    qs = np.linspace(0, 1, 201)
    for s in [0.0, 1.0, 3.0]:
        axes[0].plot(
            qs, [social_loss(float(q), 1, 1, 1, s) for q in qs], label=f"σ={s:g}"
        )
        opt = optimal_weight(1, 1, 1, s)
        axes[0].scatter([opt], [social_loss(opt, 1, 1, 1, s)])
    axes[0].set(
        xlabel="Delegated output weight q",
        ylabel="Social expected loss",
        title="Inflation bias vs stabilization",
    )
    ss = np.linspace(0, 4, 101)
    for k in [0.0, 0.5, 1.0]:
        axes[1].plot(
            ss, [optimal_weight(1, 1, k, float(s)) for s in ss], label=f"k={k:g}"
        )
    axes[1].set(
        xlabel="Shock scale σ",
        ylabel="Optimal q",
        title="Negative control: k=0 needs no conservatism",
    )
    for ax in axes:
        ax.legend()
        ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(out / "delegation.png", dpi=130)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
