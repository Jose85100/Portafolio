"""Offline connected-identity split. Links are supplied, never inferred."""

from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True)
class Record:
    record_id: str
    identities: tuple[str, ...]


def components(records: list[Record]) -> dict[str, str]:
    if len({r.record_id for r in records}) != len(records):
        raise ValueError("duplicate record IDs")
    if any(
        not r.record_id or not r.identities or any(not k for k in r.identities)
        for r in records
    ):
        raise ValueError("nonempty IDs and identities required")
    owners: dict[str, list[str]] = {}
    by_id = {r.record_id: r for r in records}
    for r in records:
        for key in set(r.identities):
            owners.setdefault(key, []).append(r.record_id)
    groups: dict[str, str] = {}
    for start in sorted(by_id):
        if start in groups:
            continue
        pending = [start]
        groups[start] = start
        seen_keys: set[str] = set()
        while pending:
            node = pending.pop()
            for key in by_id[node].identities:
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                for neighbor in owners[key]:
                    if neighbor not in groups:
                        groups[neighbor] = start
                        pending.append(neighbor)
    return groups


def split(records: list[Record], mode: str, seed: int = 0) -> dict[str, str]:
    groups = components(records)  # identical validation for all policies
    if mode == "row":
        groups = {r.record_id: r.record_id for r in records}
    elif mode == "primary":
        groups = {r.record_id: r.identities[0] for r in records}
    elif mode != "component":
        raise ValueError("unknown policy")
    keys = sorted(
        set(groups.values()), key=lambda k: (sha256(f"{seed}:{k}".encode()).digest(), k)
    )
    if len(keys) < 2:
        raise ValueError("fewer than two groups: cannot form nonempty holdout")
    train = set(keys[: len(keys) // 2])
    return {rid: "train" if group in train else "test" for rid, group in groups.items()}


def leaked_components(records: list[Record], assignment: dict[str, str]) -> int:
    groups = components(records)
    if set(groups) != set(assignment) or not set(assignment.values()) <= {
        "train",
        "test",
    }:
        raise ValueError("assignment must exactly cover records")
    sides: dict[str, set[str]] = {}
    for rid, group in groups.items():
        sides.setdefault(group, set()).add(assignment[rid])
    return sum(len(v) > 1 for v in sides.values())
