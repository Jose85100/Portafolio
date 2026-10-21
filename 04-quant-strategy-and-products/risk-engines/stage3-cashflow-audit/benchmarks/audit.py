"""Decimal oracle, actual Python parity, subprocess RSS and randomized timing."""

import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import random
import statistics
import subprocess
import tempfile
from decimal import Decimal, localcontext
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
REPO = ROOT.parents[2]
PYTHON_MODEL = REPO / (
    "03-financial-risk/01-credit-risk/credit-risk-products/"
    "ifrs9-investigacion-cuantitativa/stage3-cash-shortfall-audit/src/model.py"
)


def reference(
    gross: float, rate: float, cash: list[float], years: list[float]
) -> float:
    """Independent direct-PV formula in 100-digit Decimal, binary inputs preserved."""
    with localcontext() as ctx:
        ctx.prec = 100
        d = Decimal.from_float
        pv = sum(
            (d(c) * (-(1 + d(rate)).ln() * d(t)).exp() for c, t in zip(cash, years)),
            Decimal(0),
        )
        return float(d(gross) - pv)


def benchmark(command: list[str]) -> tuple[float, float, int, int]:
    """Linux wait4 reports each child's peak RSS, not a cumulative child maximum."""
    with tempfile.TemporaryFile(mode="w+") as output:
        child = subprocess.Popen(command, stdout=output)
        _, status, usage = os.wait4(child.pid, 0)
        child.returncode = os.waitstatus_to_exitcode(status)
        if child.returncode:
            raise RuntimeError(f"benchmark exit {child.returncode}")
        output.seek(0)
        elapsed, checksum, self_hwm = map(float, output.read().strip().split(","))
        return elapsed, checksum, usage.ru_maxrss, int(self_hwm)


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    spec = importlib.util.spec_from_file_location("stage3_python", PYTHON_MODEL)
    assert spec and spec.loader
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    cases: list[tuple[float, float, list[float], list[float]]] = []
    for gross in (1.0, 100.0, 1e6):
        for rate in (0.0, 1e-18, 1e-14, 0.01, 0.1, 1.0):
            for fraction in (0.0, 0.25, 0.5, 1.0):
                for time in (0.0, 0.5, 2.0, 30.0):
                    cases.append(
                        (gross, rate, [gross * fraction / 2] * 2, [time, time + 1])
                    )
    with (RESULTS / "fixtures.txt").open("w") as stream:
        for index, (gross, rate, cash, years) in enumerate(cases):
            stream.write(
                " ".join(map(repr, [index, gross, rate, *cash, *years])) + "\n"
            )
    command = [
        str(ROOT / "build/stage3_cli"),
        "--fixtures",
        str(RESULTS / "fixtures.txt"),
    ]
    raw = subprocess.check_output(command, text=True)
    (RESULTS / "cpp-fixtures.csv").write_text(raw)
    # Exercise the same fixtures under ASan/UBSan, not just the small unit suite.
    sanitized = subprocess.check_output(
        [str(ROOT / "build/stage3_sanitized"), *command[1:]], text=True
    )
    assert sanitized == raw
    (RESULTS / "sanitized-fixtures.csv").write_text(sanitized)
    output_rows: list[dict[str, Any]] = []
    for row in csv.DictReader(io.StringIO(raw)):
        index = int(row["id"])
        gross, rate, cash, years = cases[index]
        expected = reference(gross, rate, cash, years)
        python_value = float(model.shortfall([gross], [cash], years, rate)[0])
        stable = float(row["stable"])
        subtractive = float(row["subtractive"])
        relative = abs(stable - expected) / abs(expected) if expected else abs(stable)
        parity = abs(stable - python_value) / abs(expected) if expected else abs(stable)
        assert relative <= 1e-12 and parity <= 1e-12
        output_rows.append(
            dict(
                id=index,
                gross=gross,
                rate=rate,
                cash1=cash[0],
                cash2=cash[1],
                time1=years[0],
                time2=years[1],
                decimal=expected,
                python=python_value,
                stable=stable,
                subtractive=subtractive,
                relative_error=relative,
                python_relative_difference=parity,
            )
        )
    with (RESULTS / "accuracy.csv").open("w") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=list(output_rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(output_rows)
    # Malformed CLI invocations are rejected; no security-hardening claim.
    for arguments in (
        [],
        ["--bench", "wrong", "1", "1"],
        ["--bench", "stable", "0", "1"],
        ["--fixtures", "/nonexistent/stage3-input"],
    ):
        result = subprocess.run([command[0], *arguments], capture_output=True)
        assert result.returncode == 2
    for text in ("", "0 100 .1", "garbage"):
        with tempfile.NamedTemporaryFile(mode="w+") as fixture:
            fixture.write(text)
            fixture.flush()
            result = subprocess.run(
                [command[0], "--fixtures", fixture.name], capture_output=True
            )
            assert result.returncode == 2
    rng = random.Random(20261020)
    timings: list[dict[str, Any]] = []
    for n in (1, 128, 4096):
        for repeat in range(7):
            methods = ["stable", "subtractive"]
            rng.shuffle(methods)
            for method in methods:
                elapsed, checksum, rss, self_hwm = benchmark(
                    [command[0], "--bench", method, str(n), str(20261020 + repeat)]
                )
                timings.append(
                    dict(
                        n=n,
                        repeat=repeat,
                        method=method,
                        ms=elapsed,
                        checksum=checksum,
                        wait4_peak_rss_kib=rss,
                        process_vm_hwm_kib=self_hwm,
                    )
                )
    with (RESULTS / "performance.csv").open("w") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=list(timings[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(timings)
    summary = {
        "date": "2026-10-20",
        "seed": 20261020,
        "fixtures": len(cases),
        "max_relative_error": max(row["relative_error"] for row in output_rows),
        "max_python_relative_difference": max(
            row["python_relative_difference"] for row in output_rows
        ),
        "positive_losses_lost_to_zero_baseline": sum(
            row["decimal"] > 0 and row["subtractive"] == 0 for row in output_rows
        ),
        "positive_losses_lost_to_zero_stable": sum(
            row["decimal"] > 0 and row["stable"] == 0 for row in output_rows
        ),
        "performance_rows": len(timings),
        "medians_ms": {
            f"{n}/{method}": statistics.median(
                row["ms"]
                for row in timings
                if row["n"] == n and row["method"] == method
            )
            for n in (1, 128, 4096)
            for method in ("stable", "subtractive")
        },
        "platform": platform.platform(),
        "python_model_path": str(PYTHON_MODEL.relative_to(REPO)),
        "python_model_sha256": hashlib.sha256(PYTHON_MODEL.read_bytes()).hexdigest(),
        "fixtures_sha256": hashlib.sha256(
            (RESULTS / "fixtures.txt").read_bytes()
        ).hexdigest(),
        "cpu": next(
            line.split(":", 1)[1].strip()
            for line in Path("/proc/cpuinfo").read_text().splitlines()
            if line.startswith("model name")
        ),
        "python": platform.python_version(),
        "compiler": subprocess.check_output(
            ["g++", "--version"], text=True
        ).splitlines()[0],
        "memory_definition": "process_vm_hwm_kib: CLI /proc/self/status VmHWM after exec; wait4_peak_rss_kib may include inherited pre-exec Python RSS. Both are entire processes, not incremental kernel allocations.",
    }
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout="constrained")
    counts = [
        summary["positive_losses_lost_to_zero_baseline"],
        summary["positive_losses_lost_to_zero_stable"],
    ]
    bars = axes[0].bar(
        ["Resta directa", "C++ estable"],
        counts,
        color=["#9a6700", "#245e85"],
        edgecolor="#252525",
    )
    axes[0].bar_label(bars, padding=3)
    axes[0].set(
        title=f"Pérdidas positivas convertidas en cero\n{len(cases)} casos sintéticos",
        ylabel="Casos sintéticos",
    )
    axes[0].set_ylim(0, max(counts) * 1.2 + 1)
    for method, label, color, marker in (
        ("subtractive", "Resta directa", "#9a6700", "s"),
        ("stable", "C++ estable", "#245e85", "o"),
    ):
        axes[1].plot(
            [1, 128, 4096],
            [summary["medians_ms"][f"{n}/{method}"] for n in (1, 128, 4096)],
            label=label,
            color=color,
            marker=marker,
        )
    axes[1].set(
        xscale="log",
        xlabel="Contratos (dos flujos cada uno)",
        ylabel="Mediana por lote (ms)",
        title="Coste por lote: siete réplicas",
    )
    axes[1].set_ylim(bottom=0)
    axes[1].legend()
    fig.savefig(RESULTS / "comparison.png", dpi=140)
    fig.savefig(RESULTS / "comparison.svg")
    svg_path = RESULTS / "comparison.svg"
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_path.read_text().splitlines()) + "\n"
    )
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
