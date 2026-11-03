"""Local audit envelope around MOMENTS_V1; it does not alter the wire protocol."""

from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

from src.transport import import_state

SCHEMA = "MOMENTS_AUDIT_ENVELOPE_V1"
DIAGNOSTIC_STATES = {"tracked", "partial", "unknown"}
COUNTERS = ("rounded_to_zero", "normalization_failures", "rebase_events")


def _canonical_bytes(document: Mapping[str, Any]) -> bytes:
    """Stable serialization for this Python API, not RFC 8785/JCS."""
    return json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _validate_text(value: object, name: str) -> str:
    if type(value) is not str or not value or value.strip() != value:
        raise ValueError(f"{name} must be a non-empty trimmed string")
    return value


def create_envelope(
    payload: str,
    *,
    source_id: str,
    partition_id: str,
    diagnostic_state: str,
    diagnostic_counts: Mapping[str, int | None] | None = None,
) -> dict[str, Any]:
    """Wrap a valid V1 payload and explicit, caller-supplied audit declarations.

    Partition IDs are labels only: the function cannot prove samples are disjoint.
    Diagnostic values are caller-supplied, not inferred from a V1 payload.
    """
    if type(payload) is not str:
        raise ValueError("payload must be text")
    import_state(payload)  # reject malformed/unsupported V1 wire strings
    source = _validate_text(source_id, "source_id")
    partition = _validate_text(partition_id, "partition_id")
    if type(diagnostic_state) is not str or diagnostic_state not in DIAGNOSTIC_STATES:
        raise ValueError("diagnostic_state must be tracked, partial, or unknown")
    supplied = dict(diagnostic_counts or {})
    if set(supplied) - set(COUNTERS):
        raise ValueError("unknown diagnostic counter")
    counts: dict[str, int | None] = {}
    for name in COUNTERS:
        value = supplied.get(name)
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError(f"{name} must be a non-negative integer or null")
        counts[name] = value
    nonnull = sum(value is not None for value in counts.values())
    if diagnostic_state == "tracked" and nonnull != len(COUNTERS):
        raise ValueError("tracked diagnostics require all counters")
    if diagnostic_state == "unknown" and nonnull:
        raise ValueError("unknown diagnostics must remain null, never imply zero")
    if diagnostic_state == "partial" and (nonnull == 0 or nonnull == len(COUNTERS)):
        raise ValueError("partial diagnostics require a proper non-empty subset")

    document: dict[str, Any] = {
        "schema": SCHEMA,
        "payload": payload,
        "payload_sha256": _digest(payload.encode("ascii")),
        "provenance": {
            "source_id": source,
            "partition_id": partition,
            "partition_claim": "declared_unverified",
        },
        "diagnostics": {"state": diagnostic_state, "counts": counts},
    }
    document["envelope_sha256"] = _digest(_canonical_bytes(document))
    return document


def verify_envelope(document: Mapping[str, Any]) -> str:
    """Check schema, local envelope digest and exact V1 payload digest."""
    if not isinstance(document, Mapping):
        raise ValueError("envelope object required")
    required = {
        "schema", "payload", "payload_sha256", "provenance", "diagnostics", "envelope_sha256"
    }
    if set(document) != required or document.get("schema") != SCHEMA:
        raise ValueError("unsupported or malformed envelope schema")
    payload = document.get("payload")
    if type(payload) is not str:
        raise ValueError("payload must be text")
    import_state(payload)
    if document.get("payload_sha256") != _digest(payload.encode("ascii")):
        raise ValueError("payload digest mismatch")
    unsigned = dict(document)
    claimed = unsigned.pop("envelope_sha256")
    if type(claimed) is not str or claimed != _digest(_canonical_bytes(unsigned)):
        raise ValueError("envelope digest mismatch")
    provenance = document.get("provenance")
    if not isinstance(provenance, dict) or set(provenance) != {
        "source_id", "partition_id", "partition_claim"
    }:
        raise ValueError("malformed provenance declaration")
    _validate_text(provenance["source_id"], "source_id")
    _validate_text(provenance["partition_id"], "partition_id")
    if provenance["partition_claim"] != "declared_unverified":
        raise ValueError("partition claims are labels, not verified disjointness")
    diagnostics = document.get("diagnostics")
    if not isinstance(diagnostics, dict) or set(diagnostics) != {"state", "counts"}:
        raise ValueError("malformed diagnostics declaration")
    state, counts = diagnostics["state"], diagnostics["counts"]
    if type(state) is not str or state not in DIAGNOSTIC_STATES or not isinstance(counts, dict) or set(counts) != set(COUNTERS):
        raise ValueError("malformed diagnostics fields")
    vals = list(counts.values())
    if any(value is not None and (type(value) is not int or value < 0) for value in vals):
        raise ValueError("diagnostic counters must be non-negative integers or null")
    nonnull = sum(value is not None for value in vals)
    if (state == "tracked" and nonnull != len(COUNTERS)) or (
        state == "unknown" and nonnull != 0
    ) or (state == "partial" and nonnull in (0, len(COUNTERS))):
        raise ValueError("diagnostic state does not match available counters")
    return payload


def dumps_envelope(document: Mapping[str, Any]) -> str:
    verify_envelope(document)
    return _canonical_bytes(document).decode("utf-8")


def loads_envelope(text: str) -> dict[str, Any]:
    if type(text) is not str:
        raise ValueError("JSON text required")
    document = json.loads(text)
    verify_envelope(document)
    return document
