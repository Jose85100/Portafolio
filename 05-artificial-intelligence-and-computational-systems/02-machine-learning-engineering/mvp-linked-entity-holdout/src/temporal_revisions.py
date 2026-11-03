"""Point-in-time selection for full-replacement identity adjudication histories.

This is a local contract: it does not authenticate provenance or establish that
the identity-resolution result is correct.
"""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class Revision:
    identity: str
    revision_id: str
    available_at: str
    effective_at: str
    valid_until: str | None
    value: str


@dataclass(frozen=True)
class Selection:
    identity: str
    revision_id: str
    value: str
    status: str
    available_at: str
    effective_at: str
    valid_until: str | None


def _utc(value: str) -> datetime:
    try:
        t = datetime.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("timestamp must be timezone-aware ISO-8601") from exc
    if t.tzinfo is None or t.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware ISO-8601")
    return t.astimezone(timezone.utc)


def select_full_replacements(
    revisions: list[Revision], *, as_of: str, identity_at: str
) -> list[Selection]:
    """Select latest revision known at ``as_of``, then test its valid interval.

    The two stages are intentionally ordered. Histories must have replacement
    semantics, with one authoritative revision per identity at each transaction
    time. Ties at the latest availability instant are rejected as ambiguous.
    Valid intervals are half-open [effective_at, valid_until); None is open-ended.
    """
    known_by_as_of = _utc(as_of)
    target_time = _utc(identity_at)
    latest: dict[str, tuple[datetime, list[Revision]]] = {}
    seen_ids: set[tuple[str, str]] = set()
    for revision in revisions:
        key = (revision.identity, revision.revision_id)
        if not revision.identity or not revision.revision_id or key in seen_ids:
            raise ValueError("identity and unique revision_id required")
        seen_ids.add(key)
        available = _utc(revision.available_at)
        effective = _utc(revision.effective_at)
        end = _utc(revision.valid_until) if revision.valid_until is not None else None
        if end is not None and end <= effective:
            raise ValueError("valid_until must be later than effective_at")
        if available <= known_by_as_of:
            prior = latest.get(revision.identity)
            if prior is None or available > prior[0]:
                latest[revision.identity] = (available, [revision])
            elif available == prior[0]:
                prior[1].append(revision)

    selected: list[Selection] = []
    for identity, (_, candidates) in sorted(latest.items()):
        if len(candidates) != 1:
            raise ValueError("ambiguous latest revisions share available_at")
        revision = candidates[0]
        start = _utc(revision.effective_at)
        end = _utc(revision.valid_until) if revision.valid_until is not None else None
        active = start <= target_time and (end is None or target_time < end)
        selected.append(
            Selection(
                identity=identity,
                revision_id=revision.revision_id,
                value=revision.value,
                status="eligible" if active else "not-effective-at-identity-time",
                available_at=_utc(revision.available_at).isoformat(),
                effective_at=start.isoformat(),
                valid_until=end.isoformat() if end is not None else None,
            )
        )
    return selected


def filter_validity_first(
    revisions: list[Revision], *, as_of: str, identity_at: str
) -> list[Selection]:
    """Deliberately unsafe ablation: filter effective interval before latest."""
    known_by_as_of = _utc(as_of)
    target_time = _utc(identity_at)
    candidates = [
        r
        for r in revisions
        if _utc(r.available_at) <= known_by_as_of
        and _utc(r.effective_at) <= target_time
        and (r.valid_until is None or target_time < _utc(r.valid_until))
    ]
    latest: dict[str, Revision] = {}
    for r in candidates:
        prior = latest.get(r.identity)
        if prior is None or _utc(r.available_at) > _utc(prior.available_at):
            latest[r.identity] = r
    return [
        Selection(r.identity, r.revision_id, r.value, "eligible", _utc(r.available_at).isoformat(), _utc(r.effective_at).isoformat(), _utc(r.valid_until).isoformat() if r.valid_until else None)
        for _, r in sorted(latest.items())
    ]
