"""Independent primal SLSQP baseline and two-state scalar oracle."""

from dataclasses import dataclass
import numpy as np
from scipy.optimize import OptimizeResult, brentq, minimize
from src.kl_robust import Array, kl, validate


@dataclass(frozen=True)
class Primal:
    value: float
    q: Array
    success: bool
    message: str
    divergence: float
    mass_error: float
    iterations: int


def slsqp_reference(p: Array, loss: Array, radius: float, variant: str = "refined") -> Primal:
    p = validate(p, loss, radius)
    if variant not in ("initial", "two_start", "refined"):
        raise ValueError("unknown SLSQP variant")
    scale = max(float(np.ptp(loss)), 1.0)
    x = (loss - float(np.min(loss))) / scale

    def constraint(q: Array) -> float:
        return radius - kl(q, p)

    def constraint_jac(q: Array) -> Array:
        return -np.log(np.maximum(q, 1e-300) / p) - 1

    top = loss == np.max(loss)
    destination = np.where(top, p, 0.0) / p[top].sum()
    alpha = 0.25
    while kl((1 - alpha) * p + alpha * destination, p) > radius / 2 and alpha > 1e-12:
        alpha /= 2
    starts = (
        [p.copy()] if variant == "initial" else [p.copy(), (1 - alpha) * p + alpha * destination]
    )
    bounds = [(0.0 if variant == "initial" else float(pi * 1e-12), 1.0) for pi in p]
    constraints = [
        {"type": "eq", "fun": lambda q: float(q.sum() - 1), "jac": lambda q: np.ones_like(q)},
        {"type": "ineq", "fun": constraint, "jac": constraint_jac},
    ]

    def solve(initial: Array, tolerance: float) -> OptimizeResult:
        return minimize(
            lambda q: -float(q @ x),
            initial,
            jac=lambda q: -x,
            bounds=bounds,
            method="SLSQP",
            constraints=constraints,
            options={"ftol": tolerance, "maxiter": 1000 if variant == "initial" else 2000},
        )

    results = [solve(initial, 1e-12 if variant == "initial" else 1e-10) for initial in starts]

    def candidates() -> list[OptimizeResult]:
        return [
            res
            for res in results
            if res.success and kl(res.x, p) <= radius + 1e-8 and abs(res.x.sum() - 1) <= 1e-8
        ]

    if variant == "refined":
        # Restart the generic primal optimizer with a fresh Hessian estimate.
        # No exponential-tilt solution or binary-oracle information is used.
        best = min(candidates() or results, key=lambda res: res.fun)
        results.append(solve(np.asarray(best.x, dtype=np.float64), 1e-12))
    result = min(candidates() or results, key=lambda res: res.fun)
    q = np.asarray(result.x, dtype=np.float64)
    return Primal(
        float(q @ loss),
        q,
        bool(result.success),
        " | ".join(f"start {i}: {res.message}" for i, res in enumerate(results)),
        kl(q, p),
        abs(float(q.sum()) - 1),
        sum(int(res.nit) for res in results),
    )


def bernoulli_oracle(probability: float, radius: float) -> float:
    if not 0 < probability < 1 or not np.isfinite(radius) or radius < 0:
        raise ValueError("probability in (0,1) and nonnegative finite radius required")
    if radius == 0:
        return probability
    if radius >= -np.log(probability):
        return 1.0
    p = np.array([1 - probability, probability])
    return float(
        brentq(lambda q: kl(np.array([1 - q, q]), p) - radius, probability, 1.0, xtol=1e-14)
    )
