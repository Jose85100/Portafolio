"""Regret bounds under structured, shared payoff shocks."""

from __future__ import annotations

import math
from typing import Sequence


def shared_opponent_shock_regret(
    payoffs: Sequence[Sequence[float]],
    own: Sequence[float],
    opp: Sequence[float],
    delta: float,
) -> float:
    """Sharp regret bound if each opponent action j adds one shared shock to both rows.

    The error is epsilon[i,j] = theta[j], |theta[j]| <= delta. Since the
    deviation coefficient sums to zero across own actions, this uncertainty
    cancels exactly. Returns the nominal mixed-strategy regret.
    """
    if len(payoffs) != 2 or any(len(row) != 2 for row in payoffs):
        raise ValueError("payoff matrix must be 2x2")
    if len(own) != 2 or len(opp) != 2:
        raise ValueError("strategies must have length two")
    if any(not math.isfinite(x) for row in payoffs for x in row):
        raise ValueError("payoffs must be finite")
    if (
        any(not math.isfinite(x) or not 0 <= x <= 1 for x in (*own, *opp))
        or abs(sum(own) - 1) > 1e-12
        or abs(sum(opp) - 1) > 1e-12
    ):
        raise ValueError("strategies must be probability vectors")
    if delta < 0 or not math.isfinite(delta):
        raise ValueError("delta must be finite and nonnegative")
    gains = []
    for a in range(2):
        gains.append(
            sum(
                opp[j] * (payoffs[a][j] - sum(own[i] * payoffs[i][j] for i in range(2)))
                for j in range(2)
            )
        )
    return max(0.0, *gains)
