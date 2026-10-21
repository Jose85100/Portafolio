"""Generate deterministic validation, cost, stability and ablation outputs."""
import csv
import json
import math
import platform
import random
import sys
import time
import tracemalloc
from fractions import Fraction as F
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rootcert import isolate_quadratic, select_in_domain, verify_certificate  # noqa: E402

RESULTS = ROOT / "results"
SEED = 20261021


def write_csv(name: str, rows: list[dict[str, object]]) -> None:
    with (RESULTS / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def float_roots(a: float, b: float, c: float) -> list[float]:
    d = b * b - 4 * a * c
    if d < 0:
        return []
    return sorted([(-b - math.sqrt(d)) / (2 * a), (-b + math.sqrt(d)) / (2 * a)])


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    cases = [
        ("fire_sale", F(1), F(-1), F(4, 25), F(1, 20), F(1)),
        ("fold_double", F(1), F(-1), F(1, 4), F(1, 20), F(1)),
        ("coupled_interior", F(1), F(-23, 25), F(14, 125), F(1, 20), F(1, 5)),
        ("coupled_high", F(1), F(-1), F(18, 125), F(4, 5), F(1)),
    ]
    certificates: list[dict[str, object]] = []
    for name, a, b, c, low, high in cases:
        all_roots = isolate_quadratic(a, b, c, decimal_digits=30)
        assert verify_certificate(a, b, c, all_roots)
        selected = select_in_domain(all_roots, low, high)
        for index, root in enumerate(all_roots):
            certificates.append({
                "case": name, "root": index, "lower": str(root.lower),
                "upper": str(root.upper), "midpoint": float(root.midpoint),
                "width": float(root.width), "multiplicity": root.multiplicity,
                "inside_declared_domain": root in selected,
            })
    write_csv("certificates.csv", certificates)

    rng = random.Random(SEED)
    validation: list[dict[str, object]] = []
    max_error = 0.0
    for case in range(100):
        r1 = F(rng.randint(-1000, 800), 1000)
        r2 = r1 + F(rng.randint(1, 200), 1000)
        b, c = -(r1 + r2), r1 * r2
        exact = isolate_quadratic(F(1), b, c, decimal_digits=24)
        baseline = float_roots(1.0, float(b), float(c))
        error = max(abs(float(interval.midpoint) - root) for interval, root in zip(exact, baseline))
        max_error = max(max_error, error)
        validation.append({"case": case, "separation": float(r2-r1), "float_error": error,
                           "certificate_width_max": max(float(x.width) for x in exact)})
    write_csv("validation.csv", validation)

    stability: list[dict[str, object]] = []
    for digits in (6, 12, 18, 24, 30):
        roots = isolate_quadratic(F(1), F(-23, 25), F(14, 125), decimal_digits=digits)
        stability.append({"decimal_digits": digits, "max_width": max(float(r.width) for r in roots),
                          "verified": verify_certificate(F(1), F(-23, 25), F(14, 125), roots)})
    write_csv("stability.csv", stability)

    costs: list[dict[str, object]] = []
    for count in (100, 1000, 10000):
        samples = [(F(1), F(-1), F(i, 40000)) for i in range(1, count + 1)]
        for method in ("certificate", "float_formula"):
            durations, peaks = [], []
            for _ in range(3):
                tracemalloc.start()
                start = time.perf_counter()
                if method == "certificate":
                    output = [isolate_quadratic(a, b, c, decimal_digits=18) for a, b, c in samples]
                else:
                    output = [float_roots(float(a), float(b), float(c)) for a, b, c in samples]
                durations.append(time.perf_counter() - start)
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                peaks.append(peak)
                assert len(output) == count
            costs.append({"cases": count, "method": method, "median_seconds": sorted(durations)[1],
                          "median_peak_python_bytes": sorted(peaks)[1]})
    write_csv("costs.csv", costs)

    # Negative ablation: a sign-change grid misses an even-multiplicity root.
    grid = [F(i, 100) for i in range(5, 101)]
    sign_hits = sum(1 for left, right in zip(grid, grid[1:])
                    if (left*left-left+F(1,4)) * (right*right-right+F(1,4)) < 0)
    ablations = [{"case": "double_root_grid", "grid_intervals": 95, "sign_change_hits": sign_hits,
                  "certified_roots": 1}]
    write_csv("ablations.csv", ablations)

    metadata = {"seed": SEED, "python": sys.version, "platform": platform.platform(),
                "processor": platform.processor(), "random_cases": 100,
                "max_float_midpoint_error": max_error,
                "scope": "quadratic polynomial roots only; regime validity is separate"}
    (RESULTS / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    colors = {"certificate": "#315b7d", "float_formula": "#d28b36"}
    for method in colors:
        subset = [row for row in costs if row["method"] == method]
        axes[0].plot([int(row["cases"]) for row in subset], [float(row["median_seconds"]) for row in subset],
                     marker="o", label=method.replace("_", " "), color=colors[method])
    axes[0].set(xlabel="Quadratics", ylabel="Median time (seconds)", title="Cost of enclosure vs float baseline")
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].legend(frameon=False)
    axes[1].plot([row["decimal_digits"] for row in stability], [row["max_width"] for row in stability],
                 marker="o", color="#315b7d")
    axes[1].set(xlabel="Requested decimal digits", ylabel="Maximum interval width",
                title="Exact rational enclosure tightens predictably")
    axes[1].set_yscale("log")
    for ax in axes:
        ax.grid(axis="y", alpha=.25)
    fig.suptitle("Quadratic Root Certificate — synthetic deterministic benchmark")
    fig.tight_layout()
    fig.savefig(RESULTS / "comparison.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
