"""Exact 2x2 regret bounds for action-loaded common factors."""
from __future__ import annotations

import math
from typing import Sequence

Vector = Sequence[float]
Matrix = Sequence[Sequence[float]]


def _validate(payoffs: Matrix, own: Vector, opponent: Vector, loadings: Vector, delta: float) -> None:
    if len(payoffs) != 2 or any(len(row) != 2 for row in payoffs):
        raise ValueError("payoff matrix must be 2x2")
    if len(own) != 2 or len(opponent) != 2 or len(loadings) != 2:
        raise ValueError("strategies and loadings must have length two")
    vals = [x for row in payoffs for x in row] + list(own) + list(opponent) + list(loadings) + [delta]
    if any(not math.isfinite(x) for x in vals):
        raise ValueError("all inputs must be finite")
    if any(x < 0 or x > 1 for x in (*own, *opponent)):
        raise ValueError("strategies must be probability vectors")
    if abs(sum(own) - 1) > 1e-12 or abs(sum(opponent) - 1) > 1e-12:
        raise ValueError("strategies must sum to one")
    if delta < 0:
        raise ValueError("delta must be nonnegative")


def factor_loading_regret(payoffs: Matrix, own: Vector, opponent: Vector, loadings: Vector, delta: float) -> float:
    """Worst-case mixed regret under u_ij=A_ij+lambda_i*f_j, |f_j|<=delta."""
    _validate(payoffs, own, opponent, loadings, delta)
    worst = 0.0
    mean_loading = sum(own[i] * loadings[i] for i in range(2))
    for action in range(2):
        nominal = sum(
            opponent[j] * (payoffs[action][j] - sum(own[i] * payoffs[i][j] for i in range(2)))
            for j in range(2)
        )
        shock_support = delta * abs(loadings[action] - mean_loading) * sum(opponent)
        worst = max(worst, nominal + shock_support)
    return max(0.0, worst)


def nominal_regret(payoffs: Matrix, own: Vector, opponent: Vector) -> float:
    return factor_loading_regret(payoffs, own, opponent, (0.0, 0.0), 0.0)


def rectangular_cell_regret(payoffs: Matrix, own: Vector, opponent: Vector, delta: float) -> float:
    """Exact 2x2 upper envelope for independent cell errors |epsilon_ij|<=delta."""
    _validate(payoffs, own, opponent, (0.0, 0.0), delta)
    nominal = nominal_regret(payoffs, own, opponent)
    return nominal + 2.0 * delta * sum(opponent)
