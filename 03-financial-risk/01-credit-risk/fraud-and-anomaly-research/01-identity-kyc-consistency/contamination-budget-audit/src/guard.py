"""Finite-sample envelope assuming a supplied upper bound on contamination count."""

from bisect import bisect_left
from collections.abc import Sequence
from math import isfinite


class ContaminationGuard:
    """Frozen scores. Bound is externally supplied, never estimated from scores."""

    def __init__(self, scores: Sequence[float], max_contaminants: int = 0) -> None:
        if len(scores) == 0 or any(not isfinite(x) for x in scores):
            raise ValueError("nonempty finite scores required")
        if isinstance(max_contaminants, bool) or not isinstance(max_contaminants, int):
            raise TypeError("contamination count must be an integer")
        if not 0 <= max_contaminants < len(scores):
            raise ValueError("bound must be between zero and n-1")
        self.scores = sorted(scores)
        self.bound = max_contaminants

    def p_value(self, score: float) -> float:
        if not isfinite(score):
            raise ValueError("finite test score required")
        n = len(self.scores)
        k = n - bisect_left(self.scores, score)
        return min(1.0, (1 + k) / (n - self.bound + 1))

    def alert(self, score: float, alpha: float = 0.05) -> bool:
        if not 0 < alpha < 1:
            raise ValueError("alpha must lie in (0,1)")
        return self.p_value(score) <= alpha
