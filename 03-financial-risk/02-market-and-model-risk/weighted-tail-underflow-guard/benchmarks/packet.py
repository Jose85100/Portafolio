"""Fixed mutation corpus, negative control, and bounded receipt scaling."""

import hashlib
import json
import random
import statistics
import time
import tracemalloc
from copy import deepcopy
from pathlib import Path
from typing import Any

from benchmarks.run import write_csv
from src.consumer import decide, encode
from src.packet import MAX_BYTES, MAX_DIGITS, decode

PROJECT = Path(__file__).resolve().parents[1]


def accepts(raw: bytes, strict: bool) -> bool:
    try:
        decode(raw) if strict else json.loads(raw)
        return True
    except (ValueError, UnicodeError, RecursionError):
        return False


def mutations(p: dict[str, Any]) -> list[tuple[str, bytes]]:
    rows: list[tuple[str, bytes]] = []
    values = [
        ("breach", not p["breach"]),
        ("output_rounds_to_zero", not p["output_rounds_to_zero"]),
        ("es_float", -p["es_float"] if p["es_float"] else 1.0),
        ("backend", "unknown"),
        ("schema", "unknown"),
        ("breach", 1.0),
        ("extra", "field"),
        ("es_rational", {"numerator": "1", "denominator": "0"}),
    ]
    for i, (field, value) in enumerate(values):
        bad = deepcopy(p)
        bad[field] = value
        rows.append((f"{i}:{field}", encode(bad).encode()))
    rows.append(("duplicate_breach", (encode(p)[:-1] + ',"breach":false}').encode()))
    return rows


def main() -> None:
    out = PROJECT / "results"
    fixtures = json.loads((out / "fixtures.json").read_text())
    packets = [decide(c["losses"], "0", c["alpha"], c["weights"]) for c in fixtures]
    rejects = [
        decide([1e308, 0], "0", weights=[1e-300, 1e300], policy="raise"),
        decide([1e308, 0], "0", weights=[1e-300, 1e300], max_exact_scenarios=1),
    ]
    rows: list[dict[str, Any]] = []
    corpus: list[dict[str, Any]] = []
    for i, p in enumerate(packets + rejects):
        raw = encode(p).encode()
        assert decode(raw) == p
        rows.append(
            {
                "id": f"valid/{i}",
                "valid": True,
                "json_accepts": accepts(raw, False),
                "validator_accepts": accepts(raw, True),
                "bytes": len(raw),
            }
        )
    rng = random.Random(20261017)
    selected = []
    for backend in ["float64", "fraction"]:
        selected.extend(rng.sample([i for i, p in enumerate(packets) if p["backend"] == backend], 6))
    for i in selected:
        for name, raw in mutations(packets[i]):
            corpus.append({"id": f"mutant/{i}/{name}", "payload": raw.decode(), "expected_valid": False})
    for i, p in enumerate(rejects):
        for field, value in [("breach", False), ("reason", ""), ("es_float", 0.0)]:
            bad = deepcopy(p)
            bad[field] = value
            corpus.append({"id": f"rejected/{i}/{field}", "payload": encode(bad), "expected_valid": False})
    for case in corpus:
        raw = case["payload"].encode()
        rows.append(
            {
                "id": case["id"],
                "valid": False,
                "json_accepts": accepts(raw, False),
                "validator_accepts": accepts(raw, True),
                "bytes": len(raw),
            }
        )
    assert all(r["validator_accepts"] == r["valid"] for r in rows)
    assert all(r["json_accepts"] for r in rows)
    write_csv(out / "packet-accuracy.csv", rows)
    (out / "packet-mutations.json").write_text(json.dumps(corpus, indent=2) + "\n")
    forged = decide([1.0], "0")
    forged.update(es_float=0.0, es_rational={"numerator": "0", "denominator": "1"}, breach=False)
    assert decode(encode(forged).encode()) == forged
    (out / "packet-negative-control.json").write_text(
        json.dumps(
            {
                "original_loss": 1.0,
                "forged_packet": forged,
                "validator_accepts": True,
                "meaning": "internally consistent forgery is not detectable without provenance/recomputation",
            },
            indent=2,
        )
        + "\n"
    )
    performance: list[dict[str, Any]] = []
    for digits in [1, 32, 512, 2000]:
        raw = encode(decide([1.0], "9" * digits)).encode()
        methods = {"json_loads": lambda: json.loads(raw), "validated_receipt": lambda: decode(raw)}
        for fn in methods.values():
            fn()
        for rep in range(7):
            order = list(methods)
            rng.shuffle(order)
            for position, method in enumerate(order):
                start = time.perf_counter_ns()
                methods[method]()
                elapsed = time.perf_counter_ns() - start
                tracemalloc.start()
                methods[method]()
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                performance.append(
                    {
                        "threshold_digits": digits,
                        "bytes": len(raw),
                        "rep": rep,
                        "order": position,
                        "method": method,
                        "nanoseconds": elapsed,
                        "allocated_peak_bytes": peak,
                    }
                )
    write_csv(out / "packet-performance.csv", performance)
    summary = {
        "date": "2026-10-17",
        "seed": 20261017,
        "selected_fixture_ids": selected,
        "valid_packets": len(packets) + len(rejects),
        "invalid_mutants": len(corpus),
        "json_invalid_accepted": sum(r["json_accepts"] for r in rows if not r["valid"]),
        "validator_invalid_accepted": sum(r["validator_accepts"] for r in rows if not r["valid"]),
        "validator_valid_rejected": sum(not r["validator_accepts"] for r in rows if r["valid"]),
        "consistent_forgery_accepted": True,
        "max_bytes": MAX_BYTES,
        "max_digits": MAX_DIGITS,
        "performance_rows": len(performance),
        "source_sha256": {
            name: hashlib.sha256((PROJECT / name).read_bytes()).hexdigest()
            for name in ["src/packet.py", "benchmarks/packet.py", "results/fixtures.json"]
        },
        "medians_ms": {
            f"{d}/{m}": statistics.median(
                r["nanoseconds"] for r in performance if r["threshold_digits"] == d and r["method"] == m
            )
            / 1e6
            for d in [1, 32, 512, 2000]
            for m in ["json_loads", "validated_receipt"]
        },
    }
    (out / "packet-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
