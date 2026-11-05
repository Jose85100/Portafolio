"""Prior-concentration sensitivity for the two-price Beta-Binomial EVSI gate."""
from __future__ import annotations

from dataclasses import replace
from typing import Any

from evsi import Price, evaluate


def concentration_grid(prices: list[Price], n: int, cost: float, multipliers: list[float]) -> list[dict[str, Any]]:
    """Scale Beta prior concentrations while preserving their prior means."""
    if any(k <= 0 for k in multipliers):
        raise ValueError("concentration multipliers must be positive")
    rows = []
    for k in multipliers:
        adjusted = [replace(p, alpha=p.alpha*k, beta=p.beta*k) for p in prices]
        result = evaluate(adjusted, n, cost)
        rows.append({"concentration_multiplier": k, **result})
    return rows
