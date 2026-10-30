"""Exact row-mass holdout on frozen connected components; no labels."""

from collections import Counter
from hashlib import sha256
from src.splitter import Record, components


def validate_ratio(numerator: int, denominator: int) -> None:
    if (
        type(numerator) is not int
        or type(denominator) is not int
        or not 0 < numerator < denominator
    ):
        raise ValueError("require integer 0 < numerator < denominator")


def balanced_split(
    records: list[Record],
    numerator: int = 1,
    denominator: int = 2,
    max_rows: int = 2000,
    max_components: int = 100,
) -> dict[str, str]:
    validate_ratio(numerator, denominator)
    if type(max_rows) is not int or max_rows < 1 or len(records) > max_rows:
        raise ValueError("row budget exceeded or invalid")
    groups = components(records)
    sizes = Counter(groups.values())
    if (
        type(max_components) is not int
        or max_components < 2
        or len(sizes) > max_components
    ):
        raise ValueError("component budget exceeded or invalid")
    if len(sizes) < 2:
        raise ValueError("need at least two connected components")
    # One witness per reachable sum; old states are snapshotted (0/1, no reuse).
    witnesses: dict[int, tuple[str, ...]] = {0: ()}
    for key in sorted(sizes):
        for mass, witness in list(witnesses.items()):
            candidate = witness + (key,)
            new_mass = mass + sizes[key]
            # Any witness for a mass is sufficient for the numeric optimum.
            # Keep first reached deterministically; do not claim global lex optimum.
            if new_mass not in witnesses:
                witnesses[new_mass] = candidate
    total = len(records)
    best = min(
        (s for s in witnesses if 0 < s < total),
        key=lambda s: (abs(denominator * s - numerator * total), s),
    )
    train = set(witnesses[best])
    return {rid: "train" if group in train else "test" for rid, group in groups.items()}


def count_split(
    records: list[Record], numerator: int = 1, denominator: int = 2, seed: int = 0
) -> dict[str, str]:
    """Baseline29 generalized to requested fraction of groups, not rows."""
    validate_ratio(numerator, denominator)
    groups = components(records)
    keys = sorted(
        set(groups.values()), key=lambda k: (sha256(f"{seed}:{k}".encode()).digest(), k)
    )
    if len(keys) < 2:
        raise ValueError("need at least two connected components")
    count = max(1, min(len(keys) - 1, len(keys) * numerator // denominator))
    train = set(keys[:count])
    return {rid: "train" if group in train else "test" for rid, group in groups.items()}


def fixture(sizes: list[int]) -> list[Record]:
    if any(type(s) is not int or s < 1 for s in sizes):
        raise ValueError("positive integer sizes required")
    return [
        Record(f"g{i:03}-r{j:03}", (f"identity{i}",))
        for i, size in enumerate(sizes)
        for j in range(size)
    ]
