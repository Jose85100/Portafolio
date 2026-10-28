"""Synthetic policies, not legislation or real regulatory requirements."""

from __future__ import annotations

from src.temporal import Version


def fixture(seed: int) -> tuple[list[Version], list[dict[str, object]]]:
    key = f"synthetic-rule-{seed}"
    base = f"s{seed}"

    def v(
        name: str, value: int, vf: str, vt: str | None, kf: str, kt: str | None
    ) -> Version:
        return Version(
            key,
            f"{base}-{name}",
            f"SYNTHETIC ONLY {key}: threshold={value + seed}",
            f"synthetic://{key}/{name}",
            vf,
            vt,
            kf,
            kt,
        )

    versions = [
        v("v1", 10, "2026-01-01", None, "2026-01-01", "2026-03-01"),
        v("v2a", 12, "2026-01-01", "2026-02-01", "2026-03-01", None),
        v("v2b", 20, "2026-02-01", "2027-01-01", "2026-03-01", None),
    ]
    specs = [
        ("before_recorded", "2026-01-15", "2025-12-31", "not_found", None),
        ("old_knowledge", "2026-01-15", "2026-02-15", "ok", f"{base}-v1"),
        ("retro_corrected", "2026-01-15", "2026-04-01", "ok", f"{base}-v2a"),
        ("future_valid_old_knowledge", "2026-02-15", "2026-02-20", "ok", f"{base}-v1"),
        ("new_valid_new_knowledge", "2026-02-15", "2026-04-01", "ok", f"{base}-v2b"),
        ("expired", "2027-01-15", "2026-04-01", "not_found", None),
        ("conflict", "2026-02-15", "2026-04-01", "ambiguous", None),
    ]
    cases = []
    for name, valid, known, status, expected in specs:
        rows = versions.copy()
        if name == "conflict":
            rows.append(v("v3", 99, "2026-02-01", None, "2026-03-01", None))
        cases.append(
            {
                "case": name,
                "key": key,
                "valid_on": valid,
                "known_on": known,
                "expected_status": status,
                "expected_version": expected,
                "versions": rows,
            }
        )
    return versions, cases
