"""Balanced finite OT: feasibility, log scaling and numerical primal/dual bounds."""

from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray
from scipy.special import logsumexp

Array = NDArray[np.float64]


def validate(a: Array, b: Array, cost: Array) -> tuple[Array, Array]:
    if a.ndim != 1 or b.ndim != 1 or not a.size or not b.size:
        raise ValueError("nonempty one-dimensional masses required")
    if cost.shape != (len(a), len(b)):
        raise ValueError("cost shape must match masses")
    if not np.isfinite(a).all() or not np.isfinite(b).all() or not np.isfinite(cost).all():
        raise ValueError("finite inputs required")
    if np.min(a) < 0 or np.min(b) < 0 or np.min(cost) < 0 or np.max(cost) > 1e6:
        raise ValueError("masses >= 0; costs in [0, 1e6] required")
    if abs(float(a.sum()) - 1) > 1e-12 or abs(float(b.sum()) - 1) > 1e-12:
        raise ValueError("each mass vector must sum to 1 within 1e-12")
    return a / a.sum(), b / b.sum()


def residual(plan: Array, a: Array, b: Array) -> float:
    return float(np.abs(plan.sum(axis=1) - a).sum() + np.abs(plan.sum(axis=0) - b).sum())


def round_plan(plan: Array, a: Array, b: Array) -> Array:
    """Row/column contraction followed by rank-one residual repair (known method)."""
    a, b = validate(a, b, np.zeros((len(a), len(b))))
    if plan.shape != (len(a), len(b)) or not np.isfinite(plan).all() or np.min(plan) < 0:
        raise ValueError("finite nonnegative matching plan required")
    output = plan.copy()
    rows = output.sum(axis=1)
    row_scale = np.minimum(np.divide(a, rows, out=np.ones_like(a), where=rows > 0), 1.0)
    output *= row_scale[:, None]
    columns = output.sum(axis=0)
    col_scale = np.minimum(np.divide(b, columns, out=np.ones_like(b), where=columns > 0), 1.0)
    output *= col_scale[None, :]
    ra = np.maximum(a - output.sum(axis=1), 0.0)
    rb = np.maximum(b - output.sum(axis=0), 0.0)
    total = float(rb.sum())
    if total > 0:
        output += np.outer(ra, rb) / total
    return output


@dataclass(frozen=True)
class Transport:
    raw_plan: Array
    plan: Array
    raw_cost: float
    upper: float
    lower: float
    raw_residual: float
    rounded_residual: float
    iterations: int
    converged: bool


def sinkhorn(
    a: Array,
    b: Array,
    cost: Array,
    epsilon: float,
    method: str = "log",
    max_iterations: int = 1000,
    tolerance: float = 1e-9,
) -> Transport:
    a, b = validate(a, b, cost)
    if not np.isfinite(epsilon) or not 1e-8 <= epsilon <= 1e4:
        raise ValueError("epsilon must lie in [1e-8,1e4]")
    if (
        isinstance(max_iterations, bool)
        or not isinstance(max_iterations, int)
        or max_iterations < 1
    ):
        raise ValueError("positive integer iteration budget required")
    if not np.isfinite(tolerance) or not 0 < tolerance < 1:
        raise ValueError("tolerance must lie in (0,1)")
    if method not in ("log", "naive"):
        raise ValueError("method must be log or naive")
    ia, ib = np.flatnonzero(a > 0), np.flatnonzero(b > 0)
    aa, bb = a[ia], b[ib]
    cc = cost[np.ix_(ia, ib)]
    if method == "naive":
        kernel = np.exp(-cc / epsilon)
        u: Array = np.ones(len(aa))
        v: Array = np.ones(len(bb))
    f: Array = np.zeros(len(aa))
    g: Array = np.zeros(len(bb))
    converged = False
    for iteration in range(1, max_iterations + 1):
        if method == "log":
            f = epsilon * (np.log(aa) - logsumexp((g[None, :] - cc) / epsilon, axis=1))
            g = epsilon * (np.log(bb) - logsumexp((f[:, None] - cc) / epsilon, axis=0))
            # Gauge recentering preserves f+g and prevents pointless drift.
            gauge = float(aa @ f)
            f -= gauge
            g += gauge
            subplan = np.exp((f[:, None] + g[None, :] - cc) / epsilon)
        else:
            with np.errstate(divide="raise", invalid="raise", over="raise"):
                u = aa / (kernel @ v)
                v = bb / (kernel.T @ u)
                subplan = (u[:, None] * kernel) * v[None, :]
            f = epsilon * np.log(u)
            g = epsilon * np.log(v)
        if iteration == max_iterations or iteration % 10 == 0:
            if residual(subplan, aa, bb) <= tolerance:
                converged = True
                break
    raw = np.zeros_like(cost)
    raw[np.ix_(ia, ib)] = subplan
    rounded = round_plan(raw, a, b)
    # LP dual feasibility: subtract maximal positive violation from g.
    violation = max(float(np.max(f[:, None] + g[None, :] - cc)), 0.0)
    lower = float(aa @ f + bb @ (g - violation))
    return Transport(
        raw,
        rounded,
        float(np.sum(raw * cost)),
        float(np.sum(rounded * cost)),
        lower,
        residual(raw, a, b),
        residual(rounded, a, b),
        iteration,
        converged,
    )
