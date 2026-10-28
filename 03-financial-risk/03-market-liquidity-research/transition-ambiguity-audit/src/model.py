"""Two-regime liquidity bounds for stage/state/cash-rectangular transition ambiguity."""

import math
from collections.abc import Sequence
from dataclasses import dataclass
from functools import cache


@dataclass(frozen=True)
class Band:
    lower: float
    upper: float
    visited_states: int


def risk_band(
    cash: int,
    horizon: int,
    bounds: Sequence[Sequence[float]],
    initial: Sequence[float] = (0.8, 0.2),
) -> Band:
    """Fixed cash increments +1/-2; strict cash<0 breach, flow before transition.

    Nature may choose a row separately after observing time/cash/regime.
    This is NOT the supremum over one unknown static transition matrix.
    """
    if isinstance(cash, bool) or not isinstance(cash, int) or not 0 <= cash <= 100:
        raise ValueError("cash must be integer0..100")
    if (
        isinstance(horizon, bool)
        or not isinstance(horizon, int)
        or not 0 <= horizon <= 40
    ):
        raise ValueError("horizon must be integer0..40")
    if len(bounds) != 2 or any(len(row) != 2 for row in bounds):
        raise ValueError("two [lower,upper] row bounds required")
    if any(
        not all(math.isfinite(x) for x in row) or not 0 <= row[0] <= row[1] <= 1
        for row in bounds
    ):
        raise ValueError("finite ordered probabilities in[0,1] required")
    if (
        len(initial) != 2
        or any(not math.isfinite(x) or x < 0 for x in initial)
        or not math.isclose(math.fsum(initial), 1, rel_tol=0, abs_tol=1e-12)
    ):
        raise ValueError("initial probabilities must sum to1")

    @cache
    def value(remaining: int, balance: int, state: int) -> tuple[float, float]:
        if remaining == 0:
            return (0.0, 0.0)
        updated = balance + (1 if state == 0 else -2)
        if updated < 0:
            return (1.0, 1.0)
        if remaining == 1:
            return (0.0, 0.0)
        v0 = value(remaining - 1, updated, 0)
        v1 = value(remaining - 1, updated, 1)
        low, high = bounds[state]
        minimum = min((1 - q) * v0[0] + q * v1[0] for q in (low, high))
        maximum = max((1 - q) * v0[1] + q * v1[1] for q in (low, high))
        return minimum, maximum

    values = [value(horizon, cash, state) for state in range(2)]
    return Band(
        math.fsum(p * v[0] for p, v in zip(initial, values)),
        math.fsum(p * v[1] for p, v in zip(initial, values)),
        value.cache_info().currsize,
    )
