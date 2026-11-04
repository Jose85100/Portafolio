"""Deterministic bitemporal replay for synthetic full-replacement/delta histories."""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

Action = Literal["link", "unlink"]


@dataclass(frozen=True)
class Delta:
    edge: str
    action: Action
    effective_at: str
    available_at: str
    event_id: str


def _time(value: str) -> datetime:
    d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if d.tzinfo is None or d.utcoffset() is None:
        raise ValueError("timezone-aware ISO-8601 required")
    return d.astimezone(timezone.utc)


def replay(events: list[Delta], *, identity_at: str, cutoff: str) -> set[str]:
    """Reconstruct active edges; valid-time order within the transaction-time cutoff.

    Any conflicting max-effective-time tie abstains. Duplicate identical event IDs
    are rejected so the source ledger must be deduplicated before inference.
    """
    t, c = _time(identity_at), _time(cutoff)
    latest: dict[str, tuple[datetime, set[Action]]] = {}
    seen_ids: set[str] = set()
    for e in events:
        # Availability is the first gate: post-cutoff payload fields cannot affect
        # a historical query. The timestamp itself must remain parseable.
        available = _time(e.available_at)
        if available > c:
            continue
        if e.action not in ("link", "unlink") or not e.edge or not e.event_id:
            raise ValueError("invalid event")
        if e.event_id in seen_ids:
            raise ValueError("duplicate event_id")
        seen_ids.add(e.event_id)
        effective = _time(e.effective_at)
        if effective > t:
            continue
        old = latest.get(e.edge)
        if old is None or effective > old[0]:
            latest[e.edge] = (effective, {e.action})
        elif effective == old[0]:
            old[1].add(e.action)
    for _, actions in latest.values():
        if len(actions) > 1:
            raise ValueError("conflicting effective-time tie")
    return {edge for edge, (_, actions) in latest.items() if "link" in actions}


def snapshot_first(events: list[Delta], *, identity_at: str, cutoff: str) -> set[str]:
    """Faulty comparator: picks latest-arriving event, then checks valid time."""
    t, c = _time(identity_at), _time(cutoff)
    latest: dict[str, Delta] = {}
    for e in events:
        if _time(e.available_at) <= c:
            old = latest.get(e.edge)
            if old is None or _time(e.available_at) > _time(old.available_at):
                latest[e.edge] = e
    return {
        k
        for k, e in latest.items()
        if e.action == "link" and _time(e.effective_at) <= t
    }
