"""Small exact fixtures for temporal evidence metadata; no generation quality claim."""

from __future__ import annotations

import csv
import json
import platform
import time
import tracemalloc
from dataclasses import asdict
from pathlib import Path

from src.fixtures import fixture
from src.temporal import contains, day, select


def run() -> dict:
    cfg = json.loads(Path("config.json").read_text())
    rows = []
    inputs = []
    for seed in cfg["seeds"]:
        _, cases = fixture(seed)
        for c in cases:
            inputs.append(
                {**c, "seed": seed, "versions": [asdict(v) for v in c["versions"]]}
            )
            for mode in ("latest", "valid_only", "bitemporal"):
                tracemalloc.start()
                start = time.perf_counter()
                r = select(c["versions"], c["key"], c["valid_on"], c["known_on"], mode)
                elapsed = time.perf_counter() - start
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                v = r.citations[0].version if r.citations else None
                match = (
                    r.status == c["expected_status"]
                    and (v.version_id if v else None) == c["expected_version"]
                )
                rows.append(
                    {
                        "seed": seed,
                        "case": c["case"],
                        "mode": mode,
                        "expected_status": c["expected_status"],
                        "expected_version": c["expected_version"],
                        "status": r.status,
                        "selected": v.version_id if v else None,
                        "answer": int(v is not None),
                        "wrong_definite": int(v is not None and not match),
                        "contract_match": int(match),
                        "future_leak": int(
                            v is not None and day(v.known_from) > day(c["known_on"])
                        ),
                        "knowledge_violation": int(
                            v is not None
                            and not contains(v.known_from, v.known_to, c["known_on"])
                        ),
                        "validity_violation": int(
                            v is not None
                            and not contains(v.valid_from, v.valid_to, c["valid_on"])
                        ),
                        "payload_sha256": r.citations[0].payload_sha256 if v else None,
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
    (out / "inputs.json").write_text(json.dumps(inputs, indent=2) + "\n")
    summary = []
    for mode in ("latest", "valid_only", "bitemporal"):
        group = [r for r in rows if r["mode"] == mode]
        summary.append(
            {
                "mode": mode,
                "queries": len(group),
                "answers": sum(r["answer"] for r in group),
                "wrong_definite": sum(r["wrong_definite"] for r in group),
                "contract_matches": sum(r["contract_match"] for r in group),
                "future_leaks": sum(r["future_leak"] for r in group),
                "knowledge_violations": sum(r["knowledge_violation"] for r in group),
                "validity_violations": sum(r["validity_violation"] for r in group),
                "not_found": sum(r["status"] == "not_found" for r in group),
                "ambiguous": sum(r["status"] == "ambiguous" for r in group),
                "mean_seconds": sum(r["seconds"] for r in group) / len(group),
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
        "notes": "Finite deterministic synthetic fixture audit, not independent samples or deployed RAG accuracy. Timing includes metadata validation and tracemalloc, excludes corpus construction/notebook. Hash is not source authentication.",
    }
    (out / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="850" height="335" viewBox="0 0 850 335"><rect width="850" height="335" fill="white"/><g font-family="sans-serif" font-size="15" fill="#243746"><text x="30" y="30">Temporal evidence selection: two clocks instead of latest version</text><text x="30" y="58">Wrong definite citations (red), no citation (blue), out of 56 queries</text>'
    ]
    for i, r in enumerate(summary):
        y = 100 + i * 65
        wrong = r["wrong_definite"]
        none = r["queries"] - r["answers"]
        svg.append(
            f'<text x="30" y="{y + 17}">{r["mode"]}</text><rect x="160" y="{y}" width="{wrong * 7}" height="22" fill="#CC6677"/><rect x="{160 + wrong * 7}" y="{y}" width="{none * 7}" height="22" fill="#4477AA"/><text x="{170 + (wrong + none) * 7}" y="{y + 17}">wrong {wrong}; no citation {none}</text>'
        )
    svg.append(
        '<text x="30" y="315">Synthetic date/version metadata only; no legal interpretation or LLM evaluation.</text></g></svg>'
    )
    (out / "temporal.svg").write_text("".join(svg))
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    run()
