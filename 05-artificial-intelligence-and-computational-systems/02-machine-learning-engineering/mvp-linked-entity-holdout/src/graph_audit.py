"""Audit a frozen split against a complete adjudicated identity partition.

Pair counts concern transitive co-membership, not direct edge accuracy.
"""

from collections import Counter
from dataclasses import dataclass
from src.splitter import Record, components, leaked_components


@dataclass(frozen=True)
class GraphAudit:
    rows: int
    declared_cuts: int
    adjudicated_cuts: int
    exposed_rows: int
    true_positive_pairs: int
    false_positive_pairs: int
    false_negative_pairs: int
    true_negative_pairs: int


def choose2(n: int) -> int:
    return n * (n - 1) // 2


def audit_graph(
    observed: list[Record], truth: list[Record], assignment: dict[str, str]
) -> GraphAudit:
    """Require exact ID coverage; incomplete adjudication cannot certify safety.

    Runtime O(n log n + L), with L identity incidences, due to component
    canonicalization sorting IDs; count partition pairs through contingency
    counts, avoiding an O(n²) materialized pair table. Integer arithmetic exact.
    """
    obs, actual = components(observed), components(truth)
    if not obs or set(obs) != set(actual):
        raise ValueError("nonempty identical observed/adjudicated record IDs required")
    declared_cuts = leaked_components(observed, assignment)
    adjudicated_cuts = leaked_components(truth, assignment)
    intersections = Counter((obs[r], actual[r]) for r in obs)
    obs_sizes, true_sizes = Counter(obs.values()), Counter(actual.values())
    tp = sum(choose2(n) for n in intersections.values())
    fp = sum(choose2(n) for n in obs_sizes.values()) - tp
    fn = sum(choose2(n) for n in true_sizes.values()) - tp
    tn = choose2(len(obs)) - tp - fp - fn
    sides: dict[str, set[str]] = {}
    for rid, group in actual.items():
        sides.setdefault(group, set()).add(assignment[rid])
    exposed = sum(n for group, n in true_sizes.items() if len(sides[group]) > 1)
    return GraphAudit(
        len(obs), declared_cuts, adjudicated_cuts, exposed, tp, fp, fn, tn
    )
