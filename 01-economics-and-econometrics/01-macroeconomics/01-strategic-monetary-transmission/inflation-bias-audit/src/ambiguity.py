"""Minimax regret delegation under a known interval of shock variances."""

from __future__ import annotations
import math
from scipy.optimize import brentq
from .delegation import check, optimal_weight, social_loss


def validate_interval(
    alpha: float, weight: float, target: float, low: float, high: float
) -> None:
    check(alpha, weight, target, 0.0)
    if not all(math.isfinite(v) for v in (low, high)) or not 0 <= low <= high <= 16:
        raise ValueError("Variance interval requires 0<=low<=high<=16")


def regret(
    q: float, alpha: float, weight: float, target: float, variance: float
) -> float:
    validate_interval(alpha, weight, target, variance, variance)
    sigma = math.sqrt(variance)
    best = optimal_weight(alpha, weight, target, sigma)
    return social_loss(q, alpha, weight, target, sigma) - social_loss(
        best, alpha, weight, target, sigma
    )


def worst_regret(
    q: float, alpha: float, weight: float, target: float, low: float, high: float
) -> float:
    validate_interval(alpha, weight, target, low, high)
    return max(regret(q, alpha, weight, target, v) for v in (low, high))


def robust_weight(
    alpha: float, weight: float, target: float, low: float, high: float
) -> float:
    """Equalize endpoint regrets between endpoint-optimal delegated weights.

    Analytic reduction, not a general-purpose nonconvex optimizer. Degeneracies
    return the prior solver's convention; variance is in normalized shock units².
    """
    validate_interval(alpha, weight, target, low, high)
    left = optimal_weight(alpha, weight, target, math.sqrt(low))
    right = optimal_weight(alpha, weight, target, math.sqrt(high))
    if left == right:
        return left

    def difference(q: float) -> float:
        return regret(q, alpha, weight, target, low) - regret(
            q, alpha, weight, target, high
        )

    return float(brentq(difference, left, right, xtol=1e-14))
