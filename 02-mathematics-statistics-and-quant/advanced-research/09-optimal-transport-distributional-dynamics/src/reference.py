"""Independent HiGHS LP and one-dimensional weighted monotone coupling."""

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import eye, kron, vstack
from src.transport import Array, validate


def linear_program(a: Array, b: Array, cost: Array) -> tuple[float, Array]:
    a, b = validate(a, b, cost)
    n, m = cost.shape
    constraints = vstack(
        [kron(eye(n), np.ones((1, m))), kron(np.ones((1, n)), eye(m))], format="csr"
    )
    result = linprog(
        cost.ravel(),
        A_eq=constraints,
        b_eq=np.concatenate((a, b)),
        bounds=(0, None),
        method="highs",
        options={"primal_feasibility_tolerance": 1e-9, "dual_feasibility_tolerance": 1e-9},
    )
    if not result.success:
        raise RuntimeError(result.message)
    return float(result.fun), np.asarray(result.x.reshape(n, m))


def monotone_w2_squared(x: Array, y: Array, a: Array, b: Array) -> float:
    if x.ndim != 1 or y.ndim != 1 or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("finite one-dimensional supports required")
    cost = (x[:, None] - y[None, :]) ** 2
    a, b = validate(a, b, cost)
    order_x, order_y = np.argsort(x), np.argsort(y)
    xs, ys = x[order_x], y[order_y]
    ra, rb = a[order_x].copy(), b[order_y].copy()
    i = j = 0
    total = 0.0
    while i < len(ra) and j < len(rb):
        amount = min(ra[i], rb[j])
        total += float(amount * (xs[i] - ys[j]) ** 2)
        ra[i] -= amount
        rb[j] -= amount
        if ra[i] == 0:
            i += 1
        if rb[j] == 0:
            j += 1
    return total
