"""Reproducible comparison of plateau stopping and conditional area certification."""

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

from src.aliasing_guard import certify_area, plateau_stop, refine_sign
from src.signatures import polygon_area


def curve(t, turns, orientation):
    theta = orientation * 2 * np.pi * turns * t
    return np.column_stack([np.cos(theta), np.sin(theta)])


def save(path, rows):
    with path.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "results"
    cfg = json.loads((root / "config_guard.json").read_text())
    rows = []
    for turns in cfg["turns"]:
        for orientation in [-1, 1]:

            def fun(t, turns=turns, orientation=orientation):
                return curve(t, turns, orientation)

            for method in ["fixed8", "plateau", "certified", "certified_budget8"]:
                tracemalloc.start()
                start = time.perf_counter()
                if method == "fixed8":
                    area = polygon_area(fun(np.linspace(0, 1, 9)))
                    sign = (
                        int(np.sign(area))
                        if abs(area) > cfg["plateau_tolerance"]
                        else 0
                    )
                    n, radius = 8, float("nan")
                elif method == "plateau":
                    r = plateau_stop(
                        fun, cfg["plateau_tolerance"], max_segments=cfg["max_segments"]
                    )
                    area, sign, n, radius = r.area, r.sign, r.segments, r.radius
                else:
                    budget = 8 if method.endswith("budget8") else cfg["max_segments"]
                    r = refine_sign(fun, 2 * np.pi * turns, max_segments=budget)
                    area, sign, n, radius = r.area, r.sign, r.segments, r.radius
                elapsed = time.perf_counter() - start
                peak = tracemalloc.get_traced_memory()[1]
                tracemalloc.stop()
                rows.append(
                    dict(
                        turns=turns,
                        orientation=orientation,
                        method=method,
                        area=area,
                        true_area=orientation * np.pi * turns,
                        sign=sign,
                        segments=n,
                        radius=radius,
                        seconds=elapsed,
                        peak_python_bytes=peak,
                        wrong_sign=int(sign != 0 and sign != orientation),
                        abstained=int(sign == 0),
                        area_error=abs(area - orientation * np.pi * turns),
                    )
                )
    save(out / "guard_comparison.csv", rows)
    rng = np.random.default_rng(cfg["seed"])
    random_rows = []
    for k in range(cfg["irregular_trials"]):
        turns = int(rng.choice(cfg["turns"]))
        orientation = int(rng.choice([-1, 1]))
        n = int(rng.choice([16, 32, 64, 128]))
        t = np.r_[0, np.sort(rng.uniform(size=n - 1)), 1]
        r = certify_area(curve(t, turns, orientation), t, 2 * np.pi * turns)
        truth = orientation * np.pi * turns
        random_rows.append(
            dict(
                trial=k,
                turns=turns,
                orientation=orientation,
                segments=n,
                area=r.area,
                radius=r.radius,
                true_area=truth,
                sign=r.sign,
                enclosed=int(abs(r.area - truth) <= r.radius),
                wrong_sign=int(r.sign != 0 and r.sign != orientation),
            )
        )
    save(out / "guard_irregular.csv", random_rows)
    summary = {
        "seed": cfg["seed"],
        "cases": len(rows) // 4,
        "methods": {},
        "plateau_false_convergence": sum(
            r["method"] == "plateau"
            and r["radius"] <= cfg["plateau_tolerance"]
            and r["area_error"] > 1.0
            for r in rows
        ),
        "irregular_trials": len(random_rows),
        "irregular_enclosed": sum(r["enclosed"] for r in random_rows),
        "irregular_wrong_sign": sum(r["wrong_sign"] for r in random_rows),
        "irregular_certified": sum(r["sign"] != 0 for r in random_rows),
        "python": platform.python_version(),
        "platform": platform.platform(),
    }
    for method in ["fixed8", "plateau", "certified", "certified_budget8"]:
        group = [r for r in rows if r["method"] == method]
        summary["methods"][method] = {
            "wrong_signs": sum(r["wrong_sign"] for r in group),
            "abstentions": sum(r["abstained"] for r in group),
            "max_area_error": max(r["area_error"] for r in group),
            "mean_final_segments": float(np.mean([r["segments"] for r in group])),
            "total_seconds": sum(r["seconds"] for r in group),
        }
    assert summary["irregular_enclosed"] == cfg["irregular_trials"]
    assert summary["irregular_wrong_sign"] == 0
    assert summary["methods"]["certified"]["wrong_signs"] == 0
    assert summary["methods"]["certified"]["abstentions"] == 0
    t = np.linspace(0, 1, 9)
    false = certify_area(curve(t, 7, 1), t, 6.2)
    summary["invalid_bound_counterexample"] = {
        "supplied_L": 6.2,
        "actual_L": 14 * np.pi,
        "certified_sign": false.sign,
        "true_sign": 1,
        "area": false.area,
        "radius": false.radius,
    }
    (out / "guard_summary.json").write_text(json.dumps(summary, indent=2))
    plt.rcParams.update(
        {
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.2,
        }
    )
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for method, color in [("plateau", "#BC6536"), ("certified", "#176D9C")]:
        group = [r for r in rows if r["method"] == method and r["orientation"] == 1]
        axes[0].plot(
            [r["turns"] for r in group],
            [r["area_error"] for r in group],
            "o-",
            label=method,
            color=color,
        )
    axes[0].set(
        xlabel="Vueltas positivas del círculo",
        ylabel="Error de área al detenerse",
        title="Una meseta puede ocultar vueltas",
    )
    axes[0].legend()
    group = [r for r in random_rows if r["turns"] == 4][:20]
    axes[1].errorbar(
        range(len(group)),
        [r["area"] for r in group],
        yerr=[r["radius"] for r in group],
        fmt="o",
        capsize=2,
        color="#176D9C",
        label="Intervalo condicional",
    )
    axes[1].scatter(
        range(len(group)),
        [r["true_area"] for r in group],
        marker="x",
        color="#BC6536",
        label="Área continua exacta",
    )
    axes[1].set(
        xlabel="Primeras 20 réplicas irregulares (4 vueltas)",
        ylabel="Área orientada",
        title="Cotas conservadoras, no intervalos estadísticos",
    )
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "guard_audit.png", dpi=160)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
