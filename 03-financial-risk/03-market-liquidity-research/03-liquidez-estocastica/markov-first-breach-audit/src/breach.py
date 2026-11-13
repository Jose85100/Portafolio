"""Finite-horizon Markov cash-flow first-breach oracle; integer cash units."""

import math
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class BreachResult:
    first_breach: tuple[float, ...]
    terminal_negative: float
    survival: float
    maximum_mass_error: float
    peak_states: int

    @property
    def breach_probability(self) -> float:
        return math.fsum(self.first_breach)


def _probabilities(values: Sequence[float]) -> bool:
    return all(math.isfinite(x) and 0 <= x <= 1 for x in values) and math.isclose(
        math.fsum(values), 1, rel_tol=0, abs_tol=1e-12
    )


def first_breach(
    initial_cash: int,
    horizon: int,
    increments: Sequence[int],
    transition: Sequence[Sequence[float]],
    initial_regime: Sequence[float],
) -> BreachResult:
    """Flow at day t uses current regime; transition occurs after that day's flow.

    Breach means cash<0; zero cash survives. Absorption is measurement only,
    not an assumed liquidation policy. Terminal comparator permits recovery.
    """
    if (
        isinstance(initial_cash, bool)
        or not isinstance(initial_cash, int)
        or initial_cash < 0
    ):
        raise ValueError("initial cash must be a nonnegative integer")
    if (
        isinstance(horizon, bool)
        or not isinstance(horizon, int)
        or not 0 <= horizon <= 200
    ):
        raise ValueError("horizon must be integer0..200")
    n = len(increments)
    if not 1 <= n <= 8 or len(transition) != n or len(initial_regime) != n:
        raise ValueError("matching1..8 states required")
    if any(isinstance(x, bool) or not isinstance(x, int) for x in increments):
        raise ValueError("integer increments required")
    if max(abs(x) for x in increments) * horizon > 100000:
        raise ValueError("cash lattice range exceeds declared computational budget")
    if not _probabilities(initial_regime) or any(
        len(row) != n or not _probabilities(row) for row in transition
    ):
        raise ValueError("initial/transition probabilities must sum to1")
    alive = {
        (initial_cash, state): p for state, p in enumerate(initial_regime) if p > 0
    }
    full = alive.copy()
    first = []
    mass_error = 0.0
    peak = len(alive)
    for day in range(1, horizon + 1):
        next_alive: defaultdict[tuple[int, int], float] = defaultdict(float)
        next_full: defaultdict[tuple[int, int], float] = defaultdict(float)
        hit = 0.0
        for (cash, state), probability in alive.items():
            updated = cash + increments[state]
            if updated < 0:
                hit += probability
                continue
            for target, p in enumerate(transition[state]):
                if p > 0:
                    next_alive[updated, target] += probability * p
        for (cash, state), probability in full.items():
            updated = cash + increments[state]
            for target, p in enumerate(transition[state]):
                if p > 0:
                    next_full[updated, target] += probability * p
        alive = dict(next_alive)
        full = dict(next_full)
        first.append(hit)
        peak = max(peak, len(alive), len(full))
        mass_error = max(
            mass_error,
            abs(math.fsum(first) + math.fsum(alive.values()) - 1),
            abs(math.fsum(full.values()) - 1),
        )
    terminal = math.fsum(p for (cash, _), p in full.items() if cash < 0)
    return BreachResult(
        tuple(first), terminal, math.fsum(alive.values()), mass_error, peak
    )


def minimum_buffer(
    horizon: int,
    increments: Sequence[int],
    transition: Sequence[Sequence[float]],
    initial_regime: Sequence[float],
    target: float,
    maximum: int,
) -> int | None:
    """Small bounded grid search, no extrapolation past maximum."""
    if not math.isfinite(target) or not 0 <= target <= 1:
        raise ValueError("target must lie in[0,1]")
    if (
        isinstance(maximum, bool)
        or not isinstance(maximum, int)
        or not 0 <= maximum <= 1000
    ):
        raise ValueError("maximum buffer must be integer0..1000")
    for buffer in range(maximum + 1):
        if (
            first_breach(
                buffer, horizon, increments, transition, initial_regime
            ).breach_probability
            <= target
        ):
            return buffer
    return None
