"""Scenario-weighted Expected Shortfall Euler attribution (research MVP)."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Attribution:
    var: float
    es: float
    contributions: tuple[float, ...]
    tail_weights: tuple[float, ...]


def attribute_es(component_losses: Sequence[Sequence[float]], *, alpha: float,
                 scenario_weights: Sequence[float] | None = None) -> Attribution:
    """Allocate finite-distribution ES to additive loss components.

    Fractional boundary mass gives the exact integrated-quantile ES definition.
    Tied observations at VaR receive mass proportionally to their input weights.
    """
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be strictly between zero and one")
    if not component_losses or not component_losses[0]:
        raise ValueError("at least one scenario and component are required")
    n = len(component_losses)
    k = len(component_losses[0])
    if any(len(row) != k for row in component_losses):
        raise ValueError("component matrix must be rectangular")
    if any(not __import__("math").isfinite(x) for row in component_losses for x in row):
        raise ValueError("losses must be finite")
    weights = tuple(float(w) for w in (scenario_weights if scenario_weights is not None else [1.0] * n))
    if len(weights) != n or any(not __import__("math").isfinite(w) or w <= 0 for w in weights):
        raise ValueError("weights must be finite, positive, and match scenarios")
    total = sum(weights)
    portfolio = [sum(row) for row in component_losses]
    ordered = sorted(range(n), key=lambda i: (portfolio[i], i))
    target = alpha * total
    cumulative = 0.0
    var = portfolio[ordered[-1]]
    for i in ordered:
        cumulative += weights[i]
        if cumulative + 1e-14 >= target:
            var = portfolio[i]
            break
    tail_mass = (1.0 - alpha) * total
    above = [i for i in range(n) if portfolio[i] > var]
    mass_above = sum(weights[i] for i in above)
    boundary = [i for i in range(n) if portfolio[i] == var]
    boundary_mass = max(0.0, tail_mass - mass_above)
    mass = [0.0] * n
    for i in above:
        mass[i] = weights[i]
    if boundary:
        denom = sum(weights[i] for i in boundary)
        for i in boundary:
            mass[i] = boundary_mass * weights[i] / denom
    tail_weights = tuple(x / tail_mass for x in mass)
    contributions = tuple(sum(tail_weights[i] * component_losses[i][j] for i in range(n))
                          for j in range(k))
    return Attribution(var, sum(contributions), contributions, tail_weights)
