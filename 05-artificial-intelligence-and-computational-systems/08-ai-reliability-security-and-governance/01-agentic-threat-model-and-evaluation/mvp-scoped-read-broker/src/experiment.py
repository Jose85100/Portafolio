"""Controlled defensive fixtures, not a natural-language attack benchmark."""

from __future__ import annotations

import csv
import json
import platform
import statistics
import tempfile
import time
import tracemalloc
from pathlib import Path

from src.broker import Denied, ReadBroker
from src.fixtures import BENIGN_CASES, ESCAPE_CASES, setup


def run() -> dict:
    cfg = json.loads(Path("config.json").read_text())
    rows = []
    for seed in cfg["seeds"]:
        for case in cfg["cases"]:
            for mode in ("prefix", "resolve_then_open", "anchored_fd"):
                with tempfile.TemporaryDirectory() as tmp:
                    root, payload, hook, safe, canary = setup(Path(tmp), case, seed)
                    with ReadBroker(root, mode, cfg["max_read_bytes"]) as broker:
                        tracemalloc.start()
                        start = time.perf_counter()
                        result = None
                        reason = None
                        try:
                            result = broker.read(payload, fault_hook=hook)
                        except Denied as e:
                            reason = str(e)
                        elapsed = time.perf_counter() - start
                        _, peak = tracemalloc.get_traced_memory()
                        tracemalloc.stop()
                    rows.append(
                        {
                            "seed": seed,
                            "case": case,
                            "mode": mode,
                            "allowed": int(result is not None),
                            "denied": int(result is None),
                            "escaped_canary": int(result == canary),
                            "safe_read": int(result == safe),
                            "escape_fixture": int(case in ESCAPE_CASES),
                            "benign_fixture": int(case in BENIGN_CASES),
                            "reason": reason,
                            "seconds": elapsed,
                            "python_peak_bytes": peak,
                        }
                    )
    out = Path("results")
    out.mkdir(exist_ok=True)
    with (out / "raw.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    summary = []
    for mode in ("prefix", "resolve_then_open", "anchored_fd"):
        group = [r for r in rows if r["mode"] == mode]
        attacks = [r for r in group if r["escape_fixture"]]
        benign = [r for r in group if r["benign_fixture"]]
        summary.append(
            {
                "mode": mode,
                "requests": len(group),
                "escape_fixtures": len(attacks),
                "escaped_reads": sum(r["escaped_canary"] for r in attacks),
                "escape_rate": sum(r["escaped_canary"] for r in attacks) / len(attacks),
                "benign_requests": len(benign),
                "benign_safe_reads": sum(r["safe_read"] for r in benign),
                "utility_denial_rate": sum(r["denied"] for r in benign) / len(benign),
                "mean_seconds": statistics.mean(r["seconds"] for r in group),
                "max_python_peak_bytes": max(r["python_peak_bytes"] for r in group),
            }
        )
    result = {
        "config": cfg,
        "summary": summary,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": __import__("os").cpu_count(),
        },
        "notes": "Eight deterministic fixture repetitions vary names/content, not independent real attacks. Race is a deterministic injected interleaving after check/parent-descriptor acquisition, not probabilistic concurrency. Timings include instrumentation and are not production LLM/tool latency.",
    }
    (out / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="850" height="340" viewBox="0 0 850 340"><rect width="850" height="340" fill="white"/><g font-family="sans-serif" font-size="15" fill="#243746"><text x="30" y="30">Read-only tool authority: path strings versus anchored descriptors</text><text x="30" y="58">Outside-canary reads (red); benign utility denials (blue), percent</text>'
    ]
    for i, r in enumerate(summary):
        y = 100 + i * 65
        escape = 100 * r["escape_rate"]
        denial = 100 * r["utility_denial_rate"]
        svg.append(
            f'<text x="30" y="{y + 17}">{r["mode"]}</text><rect x="210" y="{y}" width="{escape * 2.8}" height="22" fill="#CC6677"/><rect x="{210 + escape * 2.8}" y="{y}" width="{denial * 2.8}" height="22" fill="#4477AA"/><text x="{220 + (escape + denial) * 2.8}" y="{y + 17}">escape {escape:.1f}; utility deny {denial:.1f}</text>'
        )
    svg.append(
        '<text x="30" y="320">Synthetic fixtures only; anchored policy rejects legitimate internal symlink aliases.</text></g></svg>'
    )
    (out / "authority.svg").write_text("".join(svg))
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    run()
