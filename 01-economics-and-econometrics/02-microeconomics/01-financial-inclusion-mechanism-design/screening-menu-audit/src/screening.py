"""Two-type static screening audit: quasi-linear utility and quadratic real cost."""

from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize, LinearConstraint

Array = NDArray[np.float64]


@dataclass(frozen=True)
class Economy:
    low: float = 1.0
    high: float = 2.0
    p: float = 0.2
    cost: float = 1.0

    def __post_init__(self) -> None:
        if (
            not np.isfinite([self.low, self.high, self.p, self.cost]).all()
            or not 0 < self.low < self.high
            or not 0 < self.p < 1
            or self.cost <= 0
        ):
            raise ValueError("0<low<high,0<p<1,cost>0 and finite parameters required")


def validate(menu: Array) -> Array:
    a = np.asarray(menu, dtype=float)
    if a.shape != (4,) or not np.isfinite(a).all():
        raise ValueError("Finite [qL,qH,tL,tH] required")
    return a


def slacks(menu: Array, e: Economy) -> Array:
    """IR_L,IR_H,IC_L,IC_H; weak incentive compatibility with truthful equilibrium."""
    ql, qh, tl, th = validate(menu)
    return np.array(
        [
            e.low * ql - tl,
            e.high * qh - th,
            e.low * (ql - qh) - tl + th,
            e.high * (qh - ql) - th + tl,
        ]
    )


def profit(menu: Array, e: Economy) -> float:
    ql, qh, tl, th = validate(menu)
    return float(
        (1 - e.p) * (tl - e.cost * ql**2 / 2) + e.p * (th - e.cost * qh**2 / 2)
    )


def analytic(e: Economy) -> Array:
    """Unique quantity optimum; transfers support weak IC/IR, not unique choices."""
    qh = e.high / e.cost
    ql = max(0.0, (e.low - e.p * (e.high - e.low) / (1 - e.p)) / e.cost)
    return np.array([ql, qh, e.low * ql, e.high * qh - (e.high - e.low) * ql])


def uniform(e: Economy) -> tuple[str, Array, float]:
    """Best single offered contract: pooling or high-only, not arbitrary baseline."""
    q = e.low / e.cost
    t = e.low * q
    pooling = np.array([q, q, t, t])
    pool_profit = profit(pooling, e)
    q = e.high / e.cost
    t = e.high * q
    high_only = np.array([0.0, q, 0.0, t])
    high_profit = profit(high_only, e)
    return (
        ("pooling", pooling, pool_profit)
        if pool_profit >= high_profit
        else ("high-only", high_only, high_profit)
    )


def strictify(menu: Array, e: Economy, epsilon: float = 1e-6) -> Array:
    """Tiny transfer discounts make positive allocations strictly preferred.

    Excluded low types keep zero utility. Reject discounts large enough to
    overturn the low-type IC constraint or make transfers negative.
    """
    a = validate(menu).copy()
    ql, qh, tl, th = a
    if not np.isfinite(epsilon) or epsilon <= 0:
        raise ValueError("epsilon>0 finite required")
    dl = epsilon if ql > 0 else 0.0
    dh = 2 * epsilon if ql > 0 else epsilon
    if tl < dl or th < dh or (e.high - e.low) * (qh - ql) < 4 * epsilon:
        raise ValueError("Discount too large for this menu")
    a[2] -= dl
    a[3] -= dh
    if slacks(a, e).min() < -1e-10:
        raise ValueError("Menu is not IC/IR after discount")
    return a


def qp(e: Economy) -> tuple[Array, float]:
    """Numerical oracle: concave-profit QP with linear IC/IR, no analytic start."""
    w = np.array([1 - e.p, e.p])
    A = np.array(
        [
            [e.low, 0, -1, 0],
            [0, e.high, 0, -1],
            [e.low, -e.low, -1, 1],
            [-e.high, e.high, 1, -1],
        ]
    )

    def fun(a: Array) -> float:
        return -profit(a, e)

    def jac(a: Array) -> Array:
        return np.array([w[0] * e.cost * a[0], w[1] * e.cost * a[1], -w[0], -w[1]])

    result = minimize(
        fun,
        np.zeros(4),
        jac=jac,
        constraints=[LinearConstraint(A, 0, np.inf)],
        bounds=[(0, None)] * 4,
        method="SLSQP",
        options={"ftol": 1e-12, "maxiter": 500},
    )
    if not result.success or slacks(result.x, e).min() < -1e-7:
        raise RuntimeError(str(result.message))
    return np.asarray(result.x), float(result.nit)


def realized(
    menu: Array, e: Economy, true_low: float | None = None, tie: str = "largest"
) -> float:
    """Agents choose among both contracts and outside option; stress misspecification.

    largest/smallest quantity tie break exposes nonunique weak-IC equilibrium.
    Tolerance1e-12 handles floating point, not an economic indifference band.
    """
    if tie not in ("largest", "smallest"):
        raise ValueError("Unknown tie rule")
    if true_low is not None and (not np.isfinite(true_low) or true_low <= 0):
        raise ValueError("Positive finite true type required")
    ql, qh, tl, th = validate(menu)
    qs = np.array([0.0, ql, qh])
    ts = np.array([0.0, tl, th])
    total = 0.0
    for theta, weight in [
        (e.low if true_low is None else true_low, 1 - e.p),
        (e.high, e.p),
    ]:
        utility = theta * qs - ts
        ties = np.flatnonzero(utility >= utility.max() - 1e-12)
        chosen = (
            ties[np.argmax(qs[ties])] if tie == "largest" else ties[np.argmin(qs[ties])]
        )
        total += weight * (ts[chosen] - e.cost * qs[chosen] ** 2 / 2)
    return float(total)
