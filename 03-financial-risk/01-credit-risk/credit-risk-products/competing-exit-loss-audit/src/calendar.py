"""Piecewise constant annual intensities; exact within-interval loss integration."""

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class CalendarResult:
    default_probability: float
    prepayment_probability: float
    survival: float
    exact_loss: float
    endpoint_loss: float


def project_calendar(
    durations: Sequence[float],
    default_hazard: Sequence[float],
    prepay_hazard: Sequence[float],
    ead: Sequence[float],
    lgd: float = 0.45,
    discount_force: float = 0.06,
) -> CalendarResult:
    """Durations in years, hazards/discount force in year^-1, EAD in money.

    Piecewise constant hazards and conditional EAD; no within-interval amortization.
    Endpoint comparator shares identical exit masses and calendar.
    """
    n = len(durations)
    if not 1 <= n <= 360 or any(
        len(v) != n for v in (default_hazard, prepay_hazard, ead)
    ):
        raise ValueError("matching 1..360 interval vectors required")
    if not math.isfinite(lgd) or not 0 <= lgd <= 1:
        raise ValueError("LGD in [0,1] required")
    if not math.isfinite(discount_force) or discount_force < 0:
        raise ValueError("nonnegative finite discount force required")
    for dt, d, p, exposure in zip(durations, default_hazard, prepay_hazard, ead):
        if (
            any(not math.isfinite(x) for x in (dt, d, p, exposure))
            or dt <= 0
            or min(d, p, exposure) < 0
        ):
            raise ValueError(
                "finite positive durations and nonnegative hazards/EAD required"
            )
        if not math.isfinite(d + p) or not math.isfinite((d + p + discount_force) * dt):
            raise ValueError("combined hazard-duration must be finite")
    survival, elapsed = 1.0, 0.0
    defaults, prepays, exact, endpoint = [], [], [], []
    for dt, d, p, exposure in zip(durations, default_hazard, prepay_hazard, ead):
        total = d + p
        exited = -math.expm1(-total * dt)
        dm = survival * (d / total) * exited if total else 0.0
        pm = survival * (p / total) * exited if total else 0.0
        integrated = (
            d / (total + discount_force) * (-math.expm1(-(total + discount_force) * dt))
            if total + discount_force
            else 0.0
        )
        exact.append(
            survival * exposure * lgd * math.exp(-discount_force * elapsed) * integrated
        )
        elapsed += dt
        endpoint.append(dm * exposure * lgd * math.exp(-discount_force * elapsed))
        defaults.append(dm)
        prepays.append(pm)
        survival *= math.exp(-total * dt)
    return CalendarResult(
        math.fsum(defaults),
        math.fsum(prepays),
        survival,
        math.fsum(exact),
        math.fsum(endpoint),
    )
