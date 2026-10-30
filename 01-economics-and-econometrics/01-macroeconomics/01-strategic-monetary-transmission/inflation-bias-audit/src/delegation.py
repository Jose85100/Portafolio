"""Conservative delegation: private CB objective, common social evaluation."""

from __future__ import annotations
import math
from scipy.optimize import brentq, minimize_scalar
from .monetary import validate, policies, loss


def check(alpha: float, weight: float, target: float, sigma: float) -> None:
    validate(alpha, weight, target)
    if not math.isfinite(sigma) or not 0 <= sigma <= 4:
        raise ValueError("0<=sigma<=4 required")


def social_loss(
    q: float, alpha: float, weight: float, target: float, sigma: float
) -> float:
    """Ex ante social loss for RE discretion under delegated output weight q."""
    check(alpha, weight, target, sigma)
    if not math.isfinite(q) or not 0 <= q <= 3:
        raise ValueError("0<=q<=3 required")
    return 0.5 * (
        (q * alpha * target) ** 2
        + weight * target**2
        + sigma**2 * ((q * alpha) ** 2 + weight) / (1 + q * alpha**2) ** 2
    )


def optimal_weight(alpha: float, weight: float, target: float, sigma: float) -> float:
    """Unique root on [0,weight], except all-zero objective (choose baseline)."""
    check(alpha, weight, target, sigma)
    if weight == 0 or sigma == 0 and target > 0:
        return 0.0
    if target == 0:
        return weight

    def score(q: float) -> float:
        return q * target**2 * (1 + alpha**2 * q) ** 3 + sigma**2 * (q - weight)

    return float(brentq(score, 0.0, weight, xtol=1e-14))


def oracle_weight(alpha: float, weight: float, target: float, sigma: float) -> float:
    check(alpha, weight, target, sigma)
    if weight == 0:
        return 0.0
    result = minimize_scalar(
        lambda q: social_loss(q, alpha, weight, target, sigma),
        bounds=(0.0, weight),
        method="bounded",
        options={"xatol": 1e-12},
    )
    if not result.success:
        raise RuntimeError("delegation oracle failed")
    candidates = [0.0, weight, float(result.x)]
    return min(candidates, key=lambda q: social_loss(q, alpha, weight, target, sigma))


def state_average(
    q: float, alpha: float, weight: float, target: float, sigma: float
) -> float:
    """Independent state evaluation reusing previous-cycle policy and social loss."""
    check(alpha, weight, target, sigma)
    total = 0.0
    for shock in [-sigma, sigma]:
        pi, expected = policies(shock, alpha, q, target)["discretion"]
        total += 0.5 * loss(pi, expected, shock, alpha, weight, target)
    return total
