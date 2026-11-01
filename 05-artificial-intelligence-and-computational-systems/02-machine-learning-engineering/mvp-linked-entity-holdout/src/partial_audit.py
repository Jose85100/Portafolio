"""Sharp exposure bounds given a completely adjudicated equivalence on a subset.

Unadjudicated records may join any one known class or new classes. Distinct known
classes cannot be merged. This is not valid for incomplete positive links alone.
"""

from collections import Counter
from dataclasses import dataclass
from src.splitter import Record, components, leaked_components


@dataclass(frozen=True)
class PartialAudit:
    rows: int
    adjudicated_rows: int
    unknown_rows: int
    declared_cuts: int
    lower_exposed_rows: int
    upper_exposed_rows: int
    decision: str


def partial_audit(
    observed: list[Record], adjudicated: list[Record], assignment: dict[str, str]
) -> PartialAudit:
    """Exact extrema over all equivalence completions consistent with known IDs.

    O(n log n + L) time using existing canonical components and sorted class
    sizes; O(n+L) memory, L identity incidences. Integer counts, no inference.
    """
    obs = components(observed)
    known = components(adjudicated)
    if not obs or not set(known) <= set(obs):
        raise ValueError("nonempty universe and adjudicated subset of its IDs required")
    cuts = leaked_components(observed, assignment)
    sides: dict[str, set[str]] = {}
    sizes = Counter(known.values())
    for rid, group in known.items():
        sides.setdefault(group, set()).add(assignment[rid])
    unknown = Counter(assignment[r] for r in obs if r not in known)
    lower = sum(sizes[g] for g in sides if len(sides[g]) == 2)
    if len(set(assignment.values())) < 2:
        upper = 0
    else:
        pure_train = sorted(
            (sizes[g] for g in sides if sides[g] == {"train"}), reverse=True
        )
        pure_test = sorted(
            (sizes[g] for g in sides if sides[g] == {"test"}), reverse=True
        )
        upper = (
            lower
            + sum(unknown.values())
            + sum(pure_train[: unknown["test"]])
            + sum(pure_test[: unknown["train"]])
        )
    decision = (
        "detected" if lower else ("conditional-zero" if upper == 0 else "abstain")
    )
    return PartialAudit(
        len(obs), len(known), len(obs) - len(known), cuts, lower, upper, decision
    )
