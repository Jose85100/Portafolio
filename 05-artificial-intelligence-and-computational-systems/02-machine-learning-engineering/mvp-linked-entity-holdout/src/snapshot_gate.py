"""Prospective metadata gate for the conditional partial-identity audit.

Declared provenance is not authenticated. This does not audit feature pipelines.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from src.partial_audit import PartialAudit, partial_audit
from src.splitter import Record, components, leaked_components


@dataclass(frozen=True)
class AdjudicationSnapshot:
    records: tuple[Record, ...]
    source_id: str
    schema_version: int
    semantics: str
    effective_at: str
    available_at: str


@dataclass(frozen=True)
class GateResult:
    status: str
    reasons: tuple[str, ...]
    audit: PartialAudit | None
    manifest: dict[str, object]


def utc(value: str) -> str:
    """Require aware ISO datetime and normalize offsets; naive dates are errors."""
    try:
        parsed = datetime.fromisoformat(value)
    except (ValueError, TypeError) as exc:
        raise ValueError("timezone-aware ISO8601 timestamp required") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timezone-aware ISO8601 timestamp required")
    return parsed.astimezone(timezone.utc).isoformat()


def canonical_records(records: list[Record]) -> list[dict[str, object]]:
    return [
        dict(record_id=r.record_id, identities=sorted(set(r.identities)))
        for r in sorted(records, key=lambda r: r.record_id)
    ]


def prospective_audit(
    observed: list[Record],
    assignment: dict[str, str],
    snapshot: AdjudicationSnapshot,
    cutoff: str,
) -> GateResult:
    """Block unsupported semantics/schema/source or unavailable/future snapshot.

    Both effective and availability timestamps must be <= frozen cutoff. Accepted
    means metadata-eligible, not verified truth. Snapshot payload assumed static
    valid for requested historical identity task; no changing-identity inference.
    """
    obs = components(observed)
    known = components(list(snapshot.records))
    if not obs or not set(known) <= set(obs):
        raise ValueError("nonempty observed universe and adjudicated subset required")
    leaked_components(observed, assignment)  # exact coverage and sides validation
    frozen, effective, available = (
        utc(cutoff),
        utc(snapshot.effective_at),
        utc(snapshot.available_at),
    )
    reasons: list[str] = []
    if type(snapshot.schema_version) is not int or snapshot.schema_version != 1:
        reasons.append("unsupported-schema")
    if not snapshot.source_id.strip():
        reasons.append("missing-source")
    if snapshot.semantics != "complete-equivalence-on-subset":
        reasons.append("insufficient-semantics")
    if datetime.fromisoformat(effective) > datetime.fromisoformat(frozen):
        reasons.append("future-effective")
    if datetime.fromisoformat(available) > datetime.fromisoformat(frozen):
        reasons.append("unavailable-at-cutoff")
    payload: dict[str, object] = dict(
        schema_version=snapshot.schema_version,
        source_id=snapshot.source_id,
        semantics=snapshot.semantics,
        effective_at=effective,
        available_at=available,
        cutoff=frozen,
        observed=canonical_records(observed),
        adjudicated=canonical_records(list(snapshot.records)),
        assignment=dict(assignment),
    )
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode()
    manifest: dict[str, object] = dict(
        input_sha256=sha256(encoded).hexdigest(),
        payload=payload,
        scope="declared metadata eligibility only; no source authentication or pipeline-wide guarantee",
    )
    if reasons:
        return GateResult("blocked", tuple(reasons), None, manifest)
    audit = partial_audit(observed, list(snapshot.records), assignment)
    return GateResult("metadata-eligible", (), audit, manifest)


def verify_manifest(manifest: dict[str, object]) -> bool:
    """Detect content/digest mismatch only; not authenticity or truthful provenance."""
    payload = manifest.get("payload")
    digest = manifest.get("input_sha256")
    if not isinstance(payload, dict) or not isinstance(digest, str):
        return False
    try:
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode()
    except (ValueError, TypeError):
        return False
    return sha256(encoded).hexdigest() == digest
