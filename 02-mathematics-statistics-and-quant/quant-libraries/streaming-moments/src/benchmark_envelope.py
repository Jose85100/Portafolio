"""Deterministic synthetic comparison of two metadata encodings."""

from __future__ import annotations

import csv
from hashlib import sha256
import json
from pathlib import Path
import statistics
import time

import matplotlib.pyplot as plt

from src.audit_envelope import create_envelope, dumps_envelope, loads_envelope
from src.dynamic import DynamicMoments
from src.transport import export_state

ROOT = Path(__file__).resolve().parents[1]
SEED = 831103


def baseline_sidecar(payload: str, source: str, partition: str, state: str, counts: dict[str, int | None]) -> str:
    """Flat JSON sidecar with the same claims and both integrity digests."""
    payload_digest = sha256(payload.encode("ascii")).hexdigest()
    unsigned = {
        "schema": "MOMENTS_V1_SIDECAR",
        "wire": payload,
        "wire_sha256": payload_digest,
        "source": source,
        "partition": partition,
        "partition_claim": "declared_unverified",
        "diagnostic_state": state,
        "diagnostic_counts": counts,
    }
    canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    unsigned["record_sha256"] = sha256(canonical.encode("utf-8")).hexdigest()
    return json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def verify_sidecar(record: str) -> str:
    doc = json.loads(record)
    digest = doc.pop("record_sha256")
    canonical = json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    if sha256(canonical.encode("utf-8")).hexdigest() != digest:
        raise ValueError("sidecar record digest mismatch")
    if sha256(doc["wire"].encode("ascii")).hexdigest() != doc["wire_sha256"]:
        raise ValueError("sidecar payload digest mismatch")
    return doc["wire"]


def main() -> None:
    cfg = json.loads((ROOT / "config_envelope.json").read_text())
    scenarios = []
    for i in range(cfg["scenario_count"]):
        state = ("unknown", "partial", "tracked")[i % 3]
        counts = {"rounded_to_zero": None, "normalization_failures": None, "rebase_events": None}
        if state == "partial":
            counts["rounded_to_zero"] = i % 4
        if state == "tracked":
            counts = {key: i % 2 for key in counts}
        moments = DynamicMoments()
        for j in range(i + 1):
            moments.push(((j * 37 + i * 13 + SEED) % 101 - 50) / (i + 1))
        payload = export_state(moments)
        source, partition = f"synthetic-{i:02d}", f"partition-{i % 4}"
        scenarios.append((i, payload, source, partition, state, counts))

    records: list[dict[str, object]] = []
    sizes: dict[str, list[int]] = {"envelope": [], "sidecar": []}
    latencies: dict[str, list[int]] = {"envelope": [], "sidecar": []}
    for i, payload, source, partition, state, counts in scenarios:
        for method in ("envelope", "sidecar"):
            for rep in range(cfg["repetitions"]):
                start = time.perf_counter_ns()
                if method == "envelope":
                    document = create_envelope(payload, source_id=source, partition_id=partition,
                                               diagnostic_state=state, diagnostic_counts=counts)
                    encoded = dumps_envelope(document)
                    decoded = loads_envelope(encoded)
                    recovered = decoded["payload"]
                else:
                    encoded = baseline_sidecar(payload, source, partition, state, counts)
                    recovered = verify_sidecar(encoded)
                elapsed = time.perf_counter_ns() - start
                if recovered != payload:
                    raise AssertionError("roundtrip failed")
                sizes[method].append(len(encoded.encode("utf-8")))
                latencies[method].append(elapsed)
                records.append({"scenario": i, "rep": rep, "method": method,
                                "bytes_utf8": len(encoded.encode("utf-8")), "roundtrip_ns": elapsed,
                                "diagnostic_state": state})

    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    with (out / "envelope_raw.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    summary = {
        "seed": SEED,
        "scenarios": len(scenarios),
        "repetitions_per_method": cfg["repetitions"],
        "records": len(records),
        "all_payload_roundtrips_exact": True,
        "all_metadata_states_preserved": True,
        "methods": {
            name: {"median_utf8_bytes": statistics.median(sizes[name]),
                   "median_roundtrip_ns": statistics.median(latencies[name]),
                   "p95_roundtrip_ns": sorted(latencies[name])[int(0.95 * (len(latencies[name]) - 1))]}
            for name in sizes
        },
        "interpretation": "synthetic local serialization benchmark; no throughput superiority claim",
        "baseline_semantics": "flat JSON sidecar with same fields, SHA-256 payload digest, and SHA-256 record digest",
    }
    (out / "envelope_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    labels = list(sizes)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    axes[0].bar(labels, [summary["methods"][x]["median_utf8_bytes"] for x in labels], color=["#146c94", "#8a6d3b"])
    axes[0].set_ylabel("UTF-8 serialized bytes")
    axes[0].set_title("Same metadata, two JSON layouts")
    axes[1].bar(labels, [summary["methods"][x]["median_roundtrip_ns"] for x in labels], color=["#146c94", "#8a6d3b"])
    axes[1].set_ylabel("Median serialize + verify + parse (ns)")
    axes[1].set_title("Local Python run (not cross-process)")
    for ax in axes:
        ax.grid(axis="y", alpha=.25)
        ax.tick_params(axis="x", rotation=10)
    fig.suptitle("Synthetic audit envelope versus fair JSON sidecar baseline")
    fig.tight_layout()
    fig.savefig(out / "envelope_audit.png", dpi=160)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
