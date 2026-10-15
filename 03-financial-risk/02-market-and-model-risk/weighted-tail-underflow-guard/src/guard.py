"""Conservative NumPy underflow trap with exact rational tail fallback.

Inputs mean their binary64 values. This does not guarantee every rounding error
is detected: it guards NumPy underflow events in the existing algorithm.
"""

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Literal

import numpy as np
from numpy.typing import ArrayLike

from src.sources import legacy


class TailUnderflowError(ArithmeticError):
    """Explicit refusal of a detected underflow or an oversized exact fallback."""


@dataclass(frozen=True)
class GuardedTail:
    var: float
    es: float
    tail_mass: float
    backend: Literal["float64", "fraction"]
    fallback_reason: str | None
    exact_es: Fraction | None
    output_rounds_to_zero: bool


def exact_tail(losses: ArrayLike, alpha: float = 0.975, weights: ArrayLike | None = None) -> GuardedTail:
    """Exact fractional-boundary integration, independent of the hinge oracle.

    Return ES rounded once to binary64, retaining the rational ES for audit.
    Fraction arithmetic is expensive; callers should cap fallback input size.
    """
    if not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be finite and strictly inside (0,1)")
    x = np.asarray(losses, dtype=np.float64)
    p = np.ones(x.size, dtype=np.float64) if weights is None else np.asarray(weights, dtype=np.float64)
    if x.ndim != 1 or x.size == 0 or not np.all(np.isfinite(x)):
        raise ValueError("losses must be a nonempty finite vector")
    if p.shape != x.shape or not np.all(np.isfinite(p)) or np.any(p < 0) or not np.any(p > 0):
        raise ValueError("weights must match losses, be finite, nonnegative, and have positive mass")
    atoms = sorted((Fraction(float(v)), Fraction(float(w))) for v, w in zip(x, p, strict=True) if w > 0)
    total = sum((w for _, w in atoms), Fraction())
    confidence = Fraction(alpha)
    mass = 1 - confidence
    accumulated = Fraction()
    var = atoms[-1][0]
    for value, weight in atoms:
        accumulated += weight / total
        if accumulated >= confidence:
            var = value
            break
    remaining = mass
    numerator = Fraction()
    for value, weight in reversed(atoms):
        used = min(weight / total, remaining)
        numerator += used * value
        remaining -= used
        if remaining == 0:
            break
    es = numerator / mass
    rounded = float(es)
    return GuardedTail(float(var), rounded, float(mass), "fraction", None, es, es != 0 and rounded == 0)


def guarded_tail(
    losses: ArrayLike,
    alpha: float = 0.975,
    weights: ArrayLike | None = None,
    policy: Literal["exact", "raise"] = "exact",
    max_exact_scenarios: int = 4096,
) -> GuardedTail:
    """Reuse the current algorithm; trap underflow without changing global seterr.

    `exact` recalculates from original, unnormalized inputs, not damaged weights.
    `raise` refuses the case; arrays above the exact-size cap are also refused.
    No claim of universal floating-point correctness on the fast path.
    """
    if policy not in {"exact", "raise"}:
        raise ValueError("policy must be exact or raise")
    if (
        not isinstance(max_exact_scenarios, int)
        or isinstance(max_exact_scenarios, bool)
        or max_exact_scenarios < 1
    ):
        raise ValueError("max_exact_scenarios must be a positive integer")
    try:
        with np.errstate(under="raise"):
            result = legacy.weighted_tail(losses, alpha, weights)
        return GuardedTail(
            float(result.var), float(result.es), float(result.tail_mass), "float64", None, None, False
        )
    except FloatingPointError as error:
        reason = str(error)
        if policy == "raise":
            raise TailUnderflowError(reason) from error
        if np.asarray(losses).size > max_exact_scenarios:
            raise TailUnderflowError(f"exact fallback exceeds cap={max_exact_scenarios}; {reason}") from error
        # Outside the errstate context; only original inputs reach rational math.
        result = exact_tail(losses, alpha, weights)
        return GuardedTail(
            result.var,
            result.es,
            result.tail_mass,
            result.backend,
            reason,
            result.exact_es,
            result.output_rounds_to_zero,
        )
