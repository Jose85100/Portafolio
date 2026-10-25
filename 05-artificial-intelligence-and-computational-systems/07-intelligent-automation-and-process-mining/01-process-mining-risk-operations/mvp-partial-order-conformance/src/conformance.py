"""Bounded exact conformance over unordered timestamp buckets.

Reference language is one finite sequential trace, not a general Petri net.
Events in different buckets are ordered; equal-time events have unknown order.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import permutations, product
from math import factorial
from typing import Literal

Verdict = Literal["conformant", "nonconformant", "ambiguous", "budget_exceeded"]


@dataclass(frozen=True)
class Result:
    lower: int | None
    upper: int | None
    verdict: Verdict
    realizations: int
    candidate_upper_bound: int


def distance(trace: Sequence[str], reference: Sequence[str]) -> int:
    """Insertion/deletion alignment cost; substitution equals delete+insert."""
    previous = list(range(len(reference) + 1))
    for i, label in enumerate(trace, 1):
        current = [i]
        for j, expected in enumerate(reference, 1):
            current.append(
                previous[j - 1]
                if label == expected
                else min(previous[j] + 1, current[j - 1] + 1)
            )
        previous = current
    return previous[-1]


def audit(
    buckets: Sequence[Sequence[str]],
    reference: Sequence[str],
    max_realizations: int = 720,
    max_events: int = 32,
) -> Result:
    """Enumerate all permitted orders, or explicitly refuse before enumeration.

    Factorial bound is conservative with repeated activity labels. No sampling
    or truncated enumeration is mislabeled an exact lower/upper bound.
    """
    if type(max_realizations) is not int or max_realizations < 1:
        raise ValueError("positive integer realization budget required")
    if type(max_events) is not int or max_events < 1 or max_events > 32:
        raise ValueError("event length budget must be integer in 1..32")
    if not reference or len(reference) > max_events:
        raise ValueError("reference must be nonempty and within event budget")
    if len(buckets) > max_events or sum(map(len, buckets)) > max_events:
        raise ValueError("trace exceeds event budget")
    if (
        isinstance(buckets, (str, bytes))
        or isinstance(reference, (str, bytes))
        or any(isinstance(group, (str, bytes)) for group in buckets)
    ):
        raise ValueError("structured bucket sequences and reference labels required")
    labels = [x for group in buckets for x in group] + list(reference)
    if any(not isinstance(x, str) or not x for x in labels) or any(
        not group for group in buckets
    ):
        raise ValueError("nonempty string labels and nonempty buckets required")
    bound = 1
    for group in buckets:
        bound *= factorial(len(group))
    if bound > max_realizations:
        return Result(None, None, "budget_exceeded", 0, bound)
    choices = [sorted(set(permutations(group))) for group in buckets]
    costs = []
    for groups in product(*choices):
        trace = tuple(x for group in groups for x in group)
        costs.append(distance(trace, reference))
    lower, upper = min(costs), max(costs)
    verdict: Verdict = (
        "conformant" if upper == 0 else "nonconformant" if lower > 0 else "ambiguous"
    )
    return Result(lower, upper, verdict, len(costs), bound)


def arbitrary_verdict(
    buckets: Sequence[Sequence[str]], reference: Sequence[str]
) -> str:
    """Baseline: preserve received order within tied timestamps."""
    trace = [x for group in buckets for x in group]
    return "conformant" if distance(trace, reference) == 0 else "nonconformant"
