"""Discrete cause-specific exit probabilities and discounted default loss."""

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Period:
    period: int
    active_start: float
    default_mass: float
    prepayment_mass: float
    active_end: float
    discounted_loss: float


@dataclass(frozen=True)
class Projection:
    default_probability: float
    prepayment_probability: float
    active_probability: float
    expected_loss: float
    maximum_mass_error: float
    periods: tuple[Period, ...]


def project(
    default: Sequence[float],
    prepay: Sequence[float],
    ead: Sequence[float],
    lgd: float = 0.45,
    rate: float = 0.005,
) -> Projection:
    """PD/prepay are mutually exclusive period exit probabilities given active.

    EAD is conditional exposure on default, not already multiplied by survival.
    Default/prepay are absorbing; discount is end-of-period, uniform rate.
    """
    n = len(default)
    if not 1 <= n <= 360 or len(prepay) != n or len(ead) != n:
        raise ValueError("matching1..360period vectors required")
    if (
        not math.isfinite(lgd)
        or not 0 <= lgd <= 1
        or not math.isfinite(rate)
        or not 0 <= rate <= 1
    ):
        raise ValueError("finite LGD/rate in[0,1] required")
    if any(
        not math.isfinite(d) or not math.isfinite(p) or d < 0 or p < 0 or d + p > 1
        for d, p in zip(default, prepay)
    ):
        raise ValueError("exclusive probabilities must be nonnegative and sum<=1")
    if any(not math.isfinite(x) or x < 0 for x in ead):
        raise ValueError("finite nonnegative conditional EAD required")
    active = 1.0
    rows = []
    defaults = []
    prepays = []
    losses = []
    mass_error = 0.0
    for t, (d, p, e) in enumerate(zip(default, prepay, ead), 1):
        d_mass = active * d
        p_mass = active * p
        end = active * (1 - d - p)
        term = d_mass * e * lgd / (1 + rate) ** t
        defaults.append(d_mass)
        prepays.append(p_mass)
        losses.append(term)
        rows.append(Period(t, active, d_mass, p_mass, end, term))
        mass_error = max(
            mass_error, abs(math.fsum(defaults) + math.fsum(prepays) + end - 1)
        )
        active = end
    return Projection(
        math.fsum(defaults),
        math.fsum(prepays),
        active,
        math.fsum(losses),
        mass_error,
        tuple(rows),
    )
