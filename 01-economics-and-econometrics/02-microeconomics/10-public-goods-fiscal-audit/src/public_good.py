"""Two-agent voluntary public good, matching and explicit fiscal resource cost.

Utilities: theta_i*log(1+G)-(1-s)*g_i-T_i. Lump-sum T_i are committed before
choices and sum to s*G at the predicted equilibrium only. Agents do not
internalize tax changes on deviation. Distortion lambda*s*G is an assumed
additional real resource cost, not a calibrated tax model.
"""

from __future__ import annotations
import math
from scipy.optimize import minimize_scalar


def validate(low: float, high: float, tax_cost: float) -> None:
    if (
        not all(math.isfinite(v) for v in (low, high, tax_cost))
        or not 0 < low < high <= 20
        or high <= 1
        or not 0 <= tax_cost <= 20
    ):
        raise ValueError("0<low<high<=20,high>1,0<=tax_cost<=20 required")


def no_policy(high: float) -> float:
    if not math.isfinite(high) or not 1 < high <= 20:
        raise ValueError("1<high<=20 required")
    return high - 1


def policy_welfare(
    G: float, low: float, high: float, tax_cost: float
) -> tuple[float, float, float]:
    """Return net welfare, matching share s and public transfer budget sG.

    G>=high-1 is implemented by s=1-high/(1+G). Monetary transfers cancel
    from social resources; only G plus lambda*sG are real costs here.
    """
    validate(low, high, tax_cost)
    if not math.isfinite(G) or G < no_policy(high) - 1e-12:
        raise ValueError("Nonnegative matching policy requires G>=high-1")
    s = max(0.0, 1 - high / (1 + G))
    budget = s * G
    welfare = (low + high) * math.log1p(G) - G - tax_cost * budget
    return welfare, s, budget


def optimal(low: float, high: float, tax_cost: float) -> float:
    """Closed-form optimum constrained to nonnegative matching policies."""
    validate(low, high, tax_cost)
    total = low + high
    z = (total + math.sqrt(total**2 + 4 * tax_cost * (1 + tax_cost) * high)) / (
        2 * (1 + tax_cost)
    )
    return max(no_policy(high), z - 1)


def naive(low: float, high: float) -> float:
    """Planner target under zero fiscal distortion; adverse baseline for lambda>0."""
    validate(low, high, 0)
    return low + high - 1


def oracle(low: float, high: float, tax_cost: float) -> tuple[float, float]:
    """Independent scalar optimization with explicit closed-interval endpoints."""
    validate(low, high, tax_cost)
    left, right = no_policy(high), naive(low, high)
    result = minimize_scalar(
        lambda g: -policy_welfare(g, low, high, tax_cost)[0],
        bounds=(left, right),
        method="bounded",
        options={"xatol": 1e-12},
    )
    if not result.success:
        raise RuntimeError("Scalar oracle failed")
    choices = [left, right, float(result.x)]
    best = max(choices, key=lambda g: policy_welfare(g, low, high, tax_cost)[0])
    return best, policy_welfare(best, low, high, tax_cost)[0]
