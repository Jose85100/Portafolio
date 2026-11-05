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
        # Jensen implies EVSI >= 0 in exact arithmetic. Keep the raw value visible.
        # This scale-aware diagnostic flags sub-nanounit summation residuals.
        bound = 1e-11 * max(1.0, abs(result["baseline_value"]))
        if result["evsi"] < -bound:
            raise ArithmeticError("negative EVSI exceeds the declared rounding bound")
        rows.append({"concentration_multiplier": k, **result,
                     "roundoff_bound": bound,
                     "evsi_negative_roundoff": result["evsi"] < 0})
    return rows
