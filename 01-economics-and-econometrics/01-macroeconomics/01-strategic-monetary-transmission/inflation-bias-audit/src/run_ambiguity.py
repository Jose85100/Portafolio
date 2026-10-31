"""Exact regime sweep with independent scalar minimization and performance logs."""

from typing import TypedDict
import csv
import hashlib
import json
import math
import platform
import sys
import time
import tracemalloc
from pathlib import Path
import numpy as np
import scipy
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar
from .ambiguity import robust_weight, worst_regret, regret
from .delegation import optimal_weight


class RuntimeRow(TypedDict):
    method: str
    repetition: int
    seconds: float
    python_peak_bytes: int
    q: float


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / "ambiguity-config.json").read_text())
    out = root / "results"
    rows = []
    tracemalloc.start()
    start = time.perf_counter()
    for a in config["alpha"]:
        for weight in config["weight"]:
            for k in config["target"]:
                for low, high in config["variance_intervals"]:
                    q = robust_weight(a, weight, k, low, high)
                    plug = optimal_weight(a, weight, k, math.sqrt((low + high) / 2))
                    oracle = minimize_scalar(
                        lambda z: worst_regret(z, a, weight, k, low, high),
                        bounds=(0, weight),
                        method="bounded",
                        options={"xatol": 1e-12},
                    )
                    # Independent ternary objective search refines the nonsmooth minimum.
                    # SciPy bounded has a sqrt(eps)*x stopping component near the kink.
                    loq, hiq = 0.0, float(weight)
                    for _ in range(150):
                        x1, x2 = (2 * loq + hiq) / 3, (loq + 2 * hiq) / 3
                        if worst_regret(x1, a, weight, k, low, high) < worst_regret(
                            x2, a, weight, k, low, high
                        ):
                            hiq = x2
                        else:
                            loq = x1
                    refined = worst_regret((loq + hiq) / 2, a, weight, k, low, high)
                    robust = worst_regret(q, a, weight, k, low, high)
                    exact_oracle = min(
                        float(oracle.fun),
                        refined,
                        worst_regret(0, a, weight, k, low, high),
                        worst_regret(weight, a, weight, k, low, high),
                    )
                    rows.append(
                        dict(
                            alpha=a,
                            weight=weight,
                            target=k,
                            low=low,
                            high=high,
                            robust_q=q,
                            plugin_q=plug,
                            robust_regret=robust,
                            plugin_regret=worst_regret(plug, a, weight, k, low, high),
                            oracle_regret=exact_oracle,
                            oracle_error=abs(robust - exact_oracle),
                        )
                    )
    seconds = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    with (out / "ambiguity.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    anchor = next(
        r
        for r in rows
        if (r["alpha"], r["weight"], r["target"], r["low"], r["high"])
        == (1, 1, 1, 0.04, 4)
    )
    maxerr = max(r["oracle_error"] for r in rows)
    assert maxerr < 1e-8
    assert all(r["robust_regret"] <= r["plugin_regret"] + 1e-10 for r in rows)
    runtime: list[RuntimeRow] = []
    for name, fn in [
        ("robust", lambda: robust_weight(1, 1, 1, 0.04, 4)),
        ("plugin", lambda: optimal_weight(1, 1, 1, math.sqrt(2.02))),
    ]:
        for rep in range(30):
            tracemalloc.start()
            t = time.perf_counter()
            q = fn()
            elapsed = time.perf_counter() - t
            _, mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            runtime.append(
                RuntimeRow(
                    method=name,
                    repetition=rep,
                    seconds=elapsed,
                    python_peak_bytes=mem,
                    q=q,
                )
            )
    with (out / "ambiguity-runtime.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(runtime[0]))
        w.writeheader()
        w.writerows(runtime)
    summary = dict(
        cases=len(rows),
        anchor=anchor,
        max_oracle_regret_error=maxerr,
        improved=sum(r["plugin_regret"] - r["robust_regret"] > 1e-10 for r in rows),
        seconds=seconds,
        python_peak_bytes=peak,
        hardware=platform.platform(),
        python=sys.version,
        versions=dict(
            numpy=np.__version__,
            scipy=scipy.__version__,
            matplotlib=matplotlib.__version__,
        ),
        config=config,
        data_sha256=hashlib.sha256((out / "ambiguity.csv").read_bytes()).hexdigest(),
        source_sha256=hashlib.sha256(
            (root / "src/ambiguity.py").read_bytes()
        ).hexdigest(),
        runtime={
            name: dict(
                median_seconds=float(
                    np.median([r["seconds"] for r in runtime if r["method"] == name])
                ),
                peak_bytes=max(
                    r["python_peak_bytes"] for r in runtime if r["method"] == name
                ),
            )
            for name in ["robust", "plugin"]
        },
    )
    (out / "ambiguity-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    vs = np.linspace(0.04, 4, 101)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4), layout="constrained")
    for name, q, color in [
        ("Minimax regret", anchor["robust_q"], "#0072B2"),
        ("Plug-in varianza media", anchor["plugin_q"], "#D55E00"),
    ]:
        axs[0].plot(
            vs, [regret(q, 1, 1, 1, float(v)) for v in vs], label=name, color=color
        )
    axs[0].set(
        xlabel="Varianza del shock (unidades normalizadas²)",
        ylabel="Regret social (unidades de pérdida)",
        title="El compromiso no domina punto a punto",
    )
    axs[0].legend()
    widths = np.linspace(0, 3.96, 61)
    axs[1].plot(
        widths,
        [robust_weight(1, 1, 1, 0.04, 0.04 + float(w)) for w in widths],
        color="#0072B2",
    )
    axs[1].set(
        xlabel="Amplitud del intervalo de varianza",
        ylabel="Peso delegado q",
        title="Sensibilidad: extremo inferior fijo 0,04",
    )
    fig.suptitle("Modelo sintético exacto: α=λ=k=1; sin inferencia empírica")
    fig.savefig(out / "ambiguity.png", dpi=150)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
