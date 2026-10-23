"""Synthetic audit of level-two signatures versus order-blind summaries."""

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
from src.signatures import signature, signed_area, polygon_area, circle


def save_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "results"
    cfg = json.loads((root / "config.json").read_text())
    rng = np.random.default_rng(cfg["seed"])
    rows = []
    for sd in cfg["noise_sd"]:
        for rep in range(cfg["replicates"]):
            x = circle(64) + rng.normal(0, sd, (65, 2))
            x[-1] = x[0]
            for y, path in [(1, x), (-1, x[::-1])]:
                a = signed_area(path)
                oracle = polygon_area(path)
                rows.append(
                    dict(
                        noise_sd=sd,
                        replicate=rep,
                        label=y,
                        area=a,
                        oracle=oracle,
                        signature_correct=int((1 if a >= 0 else -1) == y),
                        endpoint_correct=int(y == 1),
                        moments_correct=int(y == 1),
                    )
                )
    save_csv(out / "replicates.csv", rows)
    conv = []
    for n in cfg["n_points"]:
        a = signed_area(circle(n))
        exact = n / 2 * np.sin(2 * np.pi / n)
        conv.append(
            dict(
                segments=n,
                area=a,
                polygon_exact=exact,
                error_to_pi=abs(a - np.pi),
                oracle_error=abs(a - exact),
            )
        )
    save_csv(out / "convergence.csv", conv)
    scale = []
    for n in [64, 256, 1024, 4096]:
        x = circle(n)
        for method, fun in [("signature2", signature), ("shoelace", polygon_area)]:
            ts = []
            peaks = []
            for _ in range(3):
                tracemalloc.start()
                t = time.perf_counter()
                fun(x)
                ts.append(time.perf_counter() - t)
                peaks.append(tracemalloc.get_traced_memory()[1])
                tracemalloc.stop()
            scale.append(
                dict(
                    segments=n,
                    method=method,
                    seconds_median=float(np.median(ts)),
                    peak_bytes=max(peaks),
                )
            )
    save_csv(out / "scalability.csv", scale)
    acc = {
        str(sd): float(
            np.mean([r["signature_correct"] for r in rows if r["noise_sd"] == sd])
        )
        for sd in cfg["noise_sd"]
    }
    summary = dict(
        seed=cfg["seed"],
        samples=len(rows),
        accuracy_by_noise=acc,
        endpoint_accuracy=0.5,
        moments_accuracy=0.5,
        max_oracle_error=max(abs(r["area"] - r["oracle"]) for r in rows),
        convergence_order=float(
            np.log(conv[-2]["error_to_pi"] / conv[-1]["error_to_pi"]) / np.log(2)
        ),
        aliasing_dense_area=signed_area(circle(256, turns=2)),
        aliasing_four_segment_area=signed_area(circle(4, turns=2)),
        python=platform.python_version(),
        numpy=np.__version__,
        hardware=platform.machine(),
        platform=platform.platform(),
    )
    assert summary["max_oracle_error"] < cfg["area_tolerance"]
    assert acc["0"] >= cfg["orientation_accuracy_threshold"]
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    plt.rcParams.update(
        {
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.2,
            "font.size": 11,
        }
    )
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(
        cfg["noise_sd"],
        list(acc.values()),
        "o-",
        label="Firma nivel 2",
        color="#176D9C",
    )
    ax[0].axhline(0.5, color="#BC6536", ls="--", label="Endpoint / momentos")
    ax[0].set(
        xlabel="Ruido iid por coordenada (desv. estándar)",
        ylabel="Exactitud por nivel (200 trayectorias)",
        ylim=(0.4, 1.05),
        title="Orden de puntos: pares reversos",
    )
    ax[0].legend()
    ax[1].loglog(
        [r["segments"] for r in conv],
        [r["error_to_pi"] for r in conv],
        "o-",
        color="#176D9C",
    )
    ax[1].set(
        xlabel="Segmentos por vuelta",
        ylabel="Error absoluto de área frente a π",
        title="Error de observación: círculo poligonal",
    )
    fig.tight_layout()
    fig.savefig(out / "audit.png", dpi=160)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
