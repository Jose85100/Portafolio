"""Deterministic synthetic comparison of two metadata encodings."""

from __future__ import annotations

import csv
from hashlib import sha256
import json
from pathlib import Path
import statistics
import time

import matplotlib.pyplot as plt

from src.audit_envelope import (
    create_envelope,
    dumps_envelope,
    loads_envelope,
    validate_audit_metadata,
)
from src.dynamic import DynamicMoments
from src.transport import export_state, import_state

ROOT = Path(__file__).resolve().parents[1]
SEED = 831103


def baseline_sidecar(payload: str, source: str, partition: str, state: str, counts: dict[str, int | None]) -> str:
    """Flat JSON sidecar with the same claims and validation requirements."""
    import_state(payload)
    metadata = validate_audit_metadata(
        source, partition, "declared_unverified", state, counts
    )
    payload_digest = sha256(payload.encode("ascii")).hexdigest()
    unsigned = {
        "schema": "MOMENTS_V1_SIDECAR",
        "wire": payload,
        "wire_sha256": payload_digest,
        **metadata,
    }
    canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    unsigned["record_sha256"] = sha256(canonical.encode("utf-8")).hexdigest()
    return json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def verify_sidecar(record: str) -> dict[str, object]:
    doc = json.loads(record)
    if not isinstance(doc, dict) or set(doc) != {
        "schema", "wire", "wire_sha256", "source_id", "partition_id",
        "partition_claim", "diagnostic_state", "diagnostic_counts", "record_sha256",
    }:
        raise ValueError("sidecar schema fields mismatch")
    if doc.get("schema") != "MOMENTS_V1_SIDECAR":
        raise ValueError("unsupported sidecar schema")
    digest = doc.pop("record_sha256")
    if type(digest) is not str:
        raise ValueError("record digest must be text")
    canonical = json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    if sha256(canonical.encode("utf-8")).hexdigest() != digest:
        raise ValueError("sidecar record digest mismatch")
    if type(doc["wire"]) is not str:
        raise ValueError("wire must be text")
    import_state(doc["wire"])
    if type(doc["wire_sha256"]) is not str or sha256(doc["wire"].encode("ascii")).hexdigest() != doc["wire_sha256"]:
        raise ValueError("sidecar payload digest mismatch")
    metadata = validate_audit_metadata(
        doc["source_id"], doc["partition_id"], doc["partition_claim"],
        doc["diagnostic_state"], doc["diagnostic_counts"],
    )
    return {"payload": doc["wire"], **metadata}


def main() -> None:
    cfg = json.loads((ROOT / "config_envelope.json").read_text())
    scenarios = []
    for i in range(cfg["scenario_count"]):
        state = ("unknown", "partial", "tracked")[i % 3]
        counts: dict[str, int | None] = {
            "rounded_to_zero": None,
            "normalization_failures": None,
            "rebase_events": None,
        }
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
    payload_checks: dict[str, list[bool]] = {"envelope": [], "sidecar": []}
    metadata_checks: dict[str, dict[int, list[bool]]] = {
        name: {i: [] for i, *_ in scenarios} for name in ("envelope", "sidecar")
    }
    for i, payload, source, partition, state, counts in scenarios:
        expected = {
            "payload": payload,
            "source_id": source,
            "partition_id": partition,
            "partition_claim": "declared_unverified",
            "diagnostic_state": state,
            "diagnostic_counts": counts,
        }
        for method in ("envelope", "sidecar"):
            for rep in range(cfg["repetitions"]):
                start = time.perf_counter_ns()
                if method == "envelope":
                    document = create_envelope(payload, source_id=source, partition_id=partition,
                                               diagnostic_state=state, diagnostic_counts=counts)
                    encoded = dumps_envelope(document)
                    decoded = loads_envelope(encoded)
                    observed = {
                        "payload": decoded["payload"],
                        "source_id": decoded["provenance"]["source_id"],
                        "partition_id": decoded["provenance"]["partition_id"],
                        "partition_claim": decoded["provenance"]["partition_claim"],
                        "diagnostic_state": decoded["diagnostics"]["state"],
                        "diagnostic_counts": decoded["diagnostics"]["counts"],
                    }
                else:
                    encoded = baseline_sidecar(payload, source, partition, state, counts)
                    observed = verify_sidecar(encoded)
                elapsed = time.perf_counter_ns() - start
                payload_exact = observed["payload"] == expected["payload"]
                metadata_exact = observed == expected
                payload_checks[method].append(payload_exact)
                metadata_checks[method][i].append(metadata_exact)
                if not payload_exact or not metadata_exact:
                    raise AssertionError(f"{method} roundtrip failed for scenario {i}")
                sizes[method].append(len(encoded.encode("utf-8")))
                latencies[method].append(elapsed)
                records.append({"scenario": i, "rep": rep, "method": method,
                                "bytes_utf8": len(encoded.encode("utf-8")), "roundtrip_ns": elapsed,
                                "diagnostic_state": state,
                                "payload_exact": payload_exact,
                                "metadata_exact": metadata_exact})

    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    with (out / "envelope_raw.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    metadata_scenarios_passed = {
        name: sum(all(reps) for reps in checks.values()) for name, checks in metadata_checks.items()
    }
    metadata_records_passed = {
        name: sum(sum(reps) for reps in checks.values()) for name, checks in metadata_checks.items()
    }
    payload_records_passed = {name: sum(checks) for name, checks in payload_checks.items()}
    total_records_per_method = len(scenarios) * cfg["repetitions"]
    summary = {
        "seed": SEED,
        "scenarios": len(scenarios),
        "repetitions_per_method": cfg["repetitions"],
        "records": len(records),
        "all_payload_roundtrips_exact": all(
            passed == total_records_per_method for passed in payload_records_passed.values()
        ),
        "payload_exact_records_per_method": payload_records_passed,
        "metadata_exact_records_per_method": metadata_records_passed,
        "metadata_exact_scenarios_per_method": metadata_scenarios_passed,
        "all_metadata_states_preserved": all(
            passed == len(scenarios) for passed in metadata_scenarios_passed.values()
        ),
        "methods": {
            name: {"median_utf8_bytes": statistics.median(sizes[name]),
                   "median_roundtrip_ns": statistics.median(latencies[name]),
                   "p95_roundtrip_ns": sorted(latencies[name])[int(0.95 * (len(latencies[name]) - 1))]}
            for name in sizes
        },
        "interpretation": "synthetic local serialization benchmark; no throughput superiority claim",
        "baseline_semantics": "flat JSON sidecar with same fields, shared metadata validation, SHA-256 payload digest, and SHA-256 record digest",
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
    fig.suptitle("Synthetic audit envelope versus matched-validation JSON sidecar")
    fig.tight_layout()
    fig.savefig(out / "envelope_audit.png", dpi=160)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
