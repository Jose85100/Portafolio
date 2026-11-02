"""Transport benchmark: fair result accuracy, explicit IPC overhead and bytes."""

import csv
import json
import math
import platform
import subprocess
import time
import tracemalloc
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from src.cpp_bridge import consume
from src.transport import export_state, import_state
from src.benchmark_merge import summary, oracle


def main() -> None:
    config = json.loads(Path("config_transport.json").read_text())
    rows = []
    for seed in config["seeds"]:
        rng = np.random.default_rng(seed)
        for n in config["sizes"]:
            for e in config["exponents"]:
                xs = [
                    math.ldexp(float(x), e) for x in np.clip(rng.normal(size=n), -2, 2)
                ]
                a, b = summary(xs[: n // 2]), summary(xs[n // 2 :])
                encoded = export_state(a) + "\n" + export_state(b) + "\n"
                roundtrip = import_state(export_state(a))
                assert roundtrip.state == a.state and roundtrip.exponent == a.exponent
                raw_bytes = len(("\n".join(x.hex() for x in xs) + "\n").encode())
                scale = max(math.frexp(x)[1] for x in xs if x)
                for ddof in config["ddof"]:
                    reference = oracle(xs, ddof)
                    py = a.merge(b).result(ddof)

                    def python_merge():
                        return a.merge(b).result(ddof).std

                    def cpp_ipc():
                        return consume(a, b, ddof)[1]["std"]

                    def numpy_scaled():
                        return math.ldexp(
                            float(
                                np.std([math.ldexp(x, -scale) for x in xs], ddof=ddof)
                            ),
                            scale,
                        )

                    for name, fn in [
                        ("python_merge", python_merge),
                        ("cpp_ipc", cpp_ipc),
                        ("numpy_scaled", numpy_scaled),
                    ]:
                        timings = []
                        for _ in range(config["repeats"]):
                            start = time.perf_counter_ns()
                            answer = fn()
                            timings.append(time.perf_counter_ns() - start)
                        tracemalloc.start()
                        fn()
                        _, peak = tracemalloc.get_traced_memory()
                        tracemalloc.stop()
                        discrepancy = abs(answer - py.std)
                        rows.append(
                            dict(
                                seed=seed,
                                n=n,
                                exponent=e,
                                ddof=ddof,
                                method=name,
                                sd=answer,
                                oracle_sd=reference,
                                relative_error=abs(answer - reference) / reference,
                                python_discrepancy=discrepancy,
                                gate=discrepancy
                                <= max(4 * math.ulp(py.std), 1e-12 * abs(py.std)),
                                median_ns=float(np.median(timings)),
                                peak_python_bytes=peak,
                                summary_payload_bytes=len(encoded.encode()),
                                raw_hex_payload_bytes=raw_bytes,
                                payload_reduction=raw_bytes / len(encoded.encode()),
                            )
                        )
    with Path("results/transport_raw.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    cpp = [r for r in rows if r["method"] == "cpp_ipc"]
    output = {
        "scenarios": len(cpp),
        "rows": len(rows),
        "gate": all(r["gate"] for r in cpp),
        "max_cpp_relative_sd_error": max(r["relative_error"] for r in cpp),
        "max_python_cpp_discrepancy": max(r["python_discrepancy"] for r in cpp),
        "minimum_payload_reduction_n1024": min(
            r["payload_reduction"] for r in cpp if r["n"] == 1024
        ),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "hardware": platform.processor(),
        "compiler": subprocess.check_output(
            ["g++", "--version"], text=True
        ).splitlines()[0],
        "cmake": subprocess.check_output(
            [".venv/bin/cmake", "--version"], text=True
        ).splitlines()[0],
        "cost_scope": "python_merge excludes precomputed summaries; cpp_ipc includes export, process startup, parse/merge/output/import; NumPy includes input scan but is offline. No speedup claim. Imports/install excluded; memory Python heap only, child RSS unmeasured",
        "median_ns": {
            m: float(np.median([r["median_ns"] for r in rows if r["method"] == m]))
            for m in ["python_merge", "cpp_ipc", "numpy_scaled"]
        },
    }
    Path("results/transport_summary.json").write_text(
        json.dumps(output, indent=2) + "\n"
    )
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for method, marker in [
        ("python_merge", "o"),
        ("cpp_ipc", "x"),
        ("numpy_scaled", "+"),
    ]:
        sample = [r for r in rows if r["method"] == method]
        axes[0].scatter(
            [r["n"] for r in sample],
            [r["median_ns"] / 1000 for r in sample],
            marker=marker,
            label=method,
            alpha=0.6,
        )
    axes[0].set_yscale("log")
    axes[0].set_xlabel("Observations summarized (count)")
    axes[0].set_ylabel("Measured operation time (microseconds)")
    axes[0].legend()
    axes[0].set_title("IPC startup included; no kernel speedup claim")
    for n in config["sizes"]:
        sample = [r for r in cpp if r["n"] == n]
        axes[1].scatter(
            [n] * len(sample),
            [r["payload_reduction"] for r in sample],
            label=f"n={n}",
            alpha=0.5,
        )
    axes[1].axhline(10, color="#D55E00", ls="--", label="n1024 threshold10")
    axes[1].set_xlabel("Observations summarized (count)")
    axes[1].set_ylabel("Raw hex bytes / two summary bytes")
    axes[1].legend()
    axes[1].set_title("Synthetic inputs; no original rows transported")
    fig.tight_layout()
    fig.savefig("results/transport_audit.png", dpi=150)
    plt.close(fig)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
