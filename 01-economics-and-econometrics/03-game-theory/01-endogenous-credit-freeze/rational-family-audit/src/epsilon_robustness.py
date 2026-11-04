"""Exact worst-case regret for two-player mixed profiles under box payoff error."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class Robustness:
    nominal_regret: float
    robust_regret: float
    worst_deviation: int


def _validate(
    payoffs: Sequence[Sequence[float]],
    own: Sequence[float],
    opp: Sequence[float],
    delta: float,
) -> None:
    if len(payoffs) != 2 or any(len(row) != 2 for row in payoffs):
        raise ValueError("payoff matrix must be 2x2")
    if len(own) != 2 or len(opp) != 2:
        raise ValueError("mixed strategies must have length 2")
    if any(not 0.0 <= x <= 1.0 for x in (*own, *opp)):
        raise ValueError("probabilities must lie in [0, 1]")
    if abs(sum(own) - 1.0) > 1e-12 or abs(sum(opp) - 1.0) > 1e-12:
        raise ValueError("mixed strategies must sum to one")
    if not __import__("math").isfinite(delta) or delta < 0.0:
        raise ValueError("delta must be finite and nonnegative")
    if any(not __import__("math").isfinite(float(x)) for row in payoffs for x in row):
        raise ValueError("payoffs must be finite")


def robust_regret(
    payoffs: Sequence[Sequence[float]],
    own: Sequence[float],
    opp: Sequence[float],
    delta: float,
) -> Robustness:
    """Return exact box-uncertainty regret, where every payoff cell shifts by ±delta.

    Rows are own actions, columns opponent actions. For each pure deviation a,
    regret is E[u(a,A_-i)-u(A_i,A_-i)]. Independent cellwise errors in [-delta,delta]
    add delta times the L1 norm of the coefficient vector, giving a sharp box bound.
    """
    _validate(payoffs, own, opp, delta)
    nominal_gains: list[float] = []
    robust_gains: list[float] = []
    for deviation in range(2):
        nominal = sum(
            opp[j]
            * (payoffs[deviation][j] - sum(own[i] * payoffs[i][j] for i in range(2)))
            for j in range(2)
        )
        uncertainty = delta * sum(
            opp[j]
            * sum(abs((1.0 if i == deviation else 0.0) - own[i]) for i in range(2))
            for j in range(2)
        )
        nominal_gains.append(nominal)
        robust_gains.append(max(0.0, nominal + uncertainty))
    worst = max(range(2), key=robust_gains.__getitem__)
    return Robustness(max(0.0, *nominal_gains), robust_gains[worst], worst)
