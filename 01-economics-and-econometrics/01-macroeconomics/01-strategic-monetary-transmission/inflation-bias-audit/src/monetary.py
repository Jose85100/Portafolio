"""Linear-quadratic monetary game: commitment, discretion and RE consistency."""

from __future__ import annotations
import math
from scipy.optimize import minimize_scalar


def validate(alpha: float, weight: float, target: float) -> None:
    if (
        not all(math.isfinite(x) for x in [alpha, weight, target])
        or not 0 < alpha <= 3
        or not 0 <= weight <= 3
        or not 0 <= target <= 3
    ):
        raise ValueError("Audit domain:0<alpha<=3,0<=weight,target<=3")


def best_response(
    expected: float, shock: float, alpha: float, weight: float, target: float
) -> float:
    validate(alpha, weight, target)
    if not math.isfinite(expected) or not math.isfinite(shock):
        raise ValueError("Finite expectations and shocks required")
    return (
        weight * alpha * (alpha * expected + target - shock) / (1 + weight * alpha**2)
    )


def loss(
    pi: float, expected: float, shock: float, alpha: float, weight: float, target: float
) -> float:
    validate(alpha, weight, target)
    if not all(math.isfinite(x) for x in [pi, expected, shock]):
        raise ValueError("Finite state required")
    output = alpha * (pi - expected) + shock
    return 0.5 * (pi * pi + weight * (output - target) ** 2)


def policies(
    shock: float, alpha: float, weight: float, target: float
) -> dict[str, tuple[float, float]]:
    """Values are inflation and announced expectations, not comparable RE regimes unless consistent."""
    validate(alpha, weight, target)
    if not math.isfinite(shock):
        raise ValueError("Finite shock required")
    bias = weight * alpha * target
    response = -weight * alpha / (1 + weight * alpha**2) * shock
    return {
        "commitment": (response, 0.0),
        "discretion": (bias + response, bias),
        "naive_fixed_expectations": (
            best_response(0.0, shock, alpha, weight, target),
            0.0,
        ),
    }


def oracle(
    expected: float, shock: float, alpha: float, weight: float, target: float
) -> float:
    """Independent convex scalar loss minimization, given already-fixed expectations."""
    result = minimize_scalar(
        lambda pi: loss(pi, expected, shock, alpha, weight, target),
        bracket=(-1.0, 1.0),
        method="brent",
        options={"xtol": 1e-12},
    )
    if not result.success:
        raise RuntimeError("Numerical best response failed")
    return float(result.x)
