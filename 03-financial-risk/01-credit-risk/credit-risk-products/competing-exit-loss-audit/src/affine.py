"""Exact loss for deterministic affine conditional EAD, constant cause hazards."""
import math
from collections.abc import Sequence
from dataclasses import dataclass

from src.calendar import CalendarResult, project_calendar


@dataclass(frozen=True)
class AffineResult:
    exact_loss: float
    midpoint_loss: float
    endpoint_loss: float
    constant_start_loss: float
    default_probability: float
    prepayment_probability: float
    survival: float


def discounted_mean_fraction(x: float) -> float:
    """Mean u/dt under density proportional to exp(-x*u/dt), x>=0."""
    if not math.isfinite(x) or x < 0:
        raise ValueError("finite nonnegative hazard-duration required")
    if x < 0.01:
        return 0.5 - x / 12 + x**3 / 720 - x**5 / 30240
    if x > 700:
        return 1 / x
    return 1 / x - 1 / math.expm1(x)


def project_affine(
    durations: Sequence[float],
    default_hazard: Sequence[float],
    prepay_hazard: Sequence[float],
    ead_start: Sequence[float],
    ead_end: Sequence[float],
    lgd: float = 0.45,
    discount_force: float = 0.06,
) -> AffineResult:
    """Years, year^-1, monetary EAD endpoints; jumps at interval edges allowed.

    EAD is conditional on survival, deterministic and affine within each interval.
    Hazards are cause-specific, not Fine-Gray subdistribution hazards.
    """
    base: CalendarResult = project_calendar(
        durations, default_hazard, prepay_hazard, ead_start, lgd, discount_force
    )
    if len(ead_end) != len(durations) or any(
        not math.isfinite(v) or v < 0 for v in ead_end
    ):
        raise ValueError("matching finite nonnegative EAD endpoints required")
    exact, midpoint, endpoint = [], [], []
    survival, elapsed = 1.0, 0.0
    for dt, d, p, start, end in zip(
        durations, default_hazard, prepay_hazard, ead_start, ead_end
    ):
        a = d + p + discount_force
        x = a * dt
        weight = discounted_mean_fraction(x)
        mass = d / a * (-math.expm1(-x)) if a else 0.0
        factor = survival * lgd * math.exp(-discount_force * elapsed) * mass
        # Convex interpolation avoids subtracting large endpoint exposures.
        exact.append(factor * ((1 - weight) * start + weight * end))
        midpoint.append(factor * (0.5 * start + 0.5 * end))
        endpoint.append(factor * end)
        survival *= math.exp(-(d + p) * dt)
        elapsed += dt
    losses = [math.fsum(v) for v in (exact, midpoint, endpoint)]
    if not all(math.isfinite(v) for v in losses):
        raise ValueError("loss outside finite float range")
    return AffineResult(losses[0], losses[1], losses[2], base.exact_loss, base.default_probability,
                        base.prepayment_probability, base.survival)
