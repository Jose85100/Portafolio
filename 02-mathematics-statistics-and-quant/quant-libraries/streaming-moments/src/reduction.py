"""Deterministic balanced reduction for disjoint dynamic-moment summaries."""

from collections.abc import Iterable
from src.dynamic import DynamicMoments


def merge_balanced(states: Iterable[DynamicMoments]) -> DynamicMoments:
    """Merge in a fixed pairwise tree; odd tail carries to the next level.

    This fixes a reduction order, not a universal accuracy guarantee. Inputs
    must represent disjoint observations. Empty input returns the identity.
    """
    level = list(states)
    if not level:
        return DynamicMoments()
    while len(level) > 1:
        next_level = [level[i].merge(level[i + 1]) for i in range(0, len(level) - 1, 2)]
        if len(level) % 2:
            next_level.append(level[-1])
        level = next_level
    return level[0]
