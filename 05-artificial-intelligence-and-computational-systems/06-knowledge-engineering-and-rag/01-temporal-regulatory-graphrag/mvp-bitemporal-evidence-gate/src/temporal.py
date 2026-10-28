"""Bitemporal evidence filtering; no LLM, graph, semantic or legal reasoning."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import date
from hashlib import sha256
from typing import Literal

Mode = Literal["latest", "valid_only", "bitemporal"]


def day(value: str) -> date:
    if not isinstance(value, str):
        raise TypeError("ISO date string required")
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("canonical YYYY-MM-DD required")
    return parsed


def contains(start: str, end: str | None, value: str) -> bool:
    return day(start) <= day(value) and (end is None or day(value) < day(end))


@dataclass(frozen=True)
class Version:
    key: str
    version_id: str
    text: str
    source: str
    valid_from: str
    valid_to: str | None
    known_from: str
    known_to: str | None

    def validate(self) -> None:
        if not all(
            isinstance(x, str) and x
            for x in (self.key, self.version_id, self.text, self.source)
        ):
            raise ValueError("nonempty evidence fields required")
        for start, end in (
            (self.valid_from, self.valid_to),
            (self.known_from, self.known_to),
        ):
            begin = day(start)
            if end is not None and day(end) <= begin:
                raise ValueError("interval must be nonempty [start,end)")


@dataclass(frozen=True)
class Citation:
    version: Version
    payload_sha256: str


@dataclass(frozen=True)
class Result:
    status: Literal["ok", "not_found", "ambiguous"]
    citations: tuple[Citation, ...]
    candidate_ids: tuple[str, ...]


def digest(version: Version) -> str:
    raw = json.dumps(
        asdict(version), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return sha256(raw.encode()).hexdigest()


def integrity_ok(citation: Citation) -> bool:
    """Content fingerprint, not signature or proof that source metadata is true."""
    return digest(citation.version) == citation.payload_sha256


def select(
    versions: Sequence[Version],
    key: str,
    valid_on: str,
    known_on: str,
    mode: Mode = "bitemporal",
) -> Result:
    if mode not in ("latest", "valid_only", "bitemporal"):
        raise ValueError("unknown policy")
    if not isinstance(key, str) or not key:
        raise ValueError("nonempty key required")
    day(valid_on)
    day(known_on)
    ids = set()
    for version in versions:
        version.validate()
        if version.version_id in ids:
            raise ValueError("duplicate version identity")
        ids.add(version.version_id)
    candidates = [v for v in versions if v.key == key]
    if mode in ("valid_only", "bitemporal"):
        candidates = [
            v for v in candidates if contains(v.valid_from, v.valid_to, valid_on)
        ]
    if mode == "bitemporal":
        candidates = [
            v for v in candidates if contains(v.known_from, v.known_to, known_on)
        ]
    if not candidates:
        return Result("not_found", (), ())
    candidate_ids = tuple(sorted(v.version_id for v in candidates))
    if mode == "bitemporal" and len(candidates) > 1:
        return Result("ambiguous", (), candidate_ids)
    # Deliberate baseline: current latest version with arbitrary version-ID tie break.
    chosen = max(candidates, key=lambda v: (day(v.known_from), v.version_id))
    return Result("ok", (Citation(chosen, digest(chosen)),), candidate_ids)
