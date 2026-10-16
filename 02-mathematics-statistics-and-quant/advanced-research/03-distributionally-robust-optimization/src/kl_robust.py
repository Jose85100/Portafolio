"""Finite-support KL(q||p) robust expectations with numerical primal/dual diagnostics."""

from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray
from scipy.special import logsumexp, xlogy

Array = NDArray[np.float64]


def validate(p: Array, loss: Array, radius: float) -> Array:
    if p.ndim != 1 or loss.shape != p.shape or not p.size:
        raise ValueError("matching nonempty vectors required")
    if not np.isfinite(p).all() or not np.isfinite(loss).all():
        raise ValueError("finite p and losses required")
    if np.min(p) < 1e-12 or abs(float(p.sum()) - 1) > 1e-12:
        raise ValueError("p_i >= 1e-12 and sum(p) within 1e-12 of 1 required")
    if (
        np.max(np.abs(loss)) > 1e6
        or not np.isfinite(radius)
        or not (radius == 0 or 1e-10 <= radius <= 100)
    ):
        raise ValueError("absolute losses <=1e6; radius must be zero or in [1e-10,100]")
    return p / p.sum()


def kl(q: Array, p: Array) -> float:
    """Finite relative entropy; zero q entries contribute zero."""
    return float(np.sum(xlogy(q, q / p)))


@dataclass(frozen=True)
class Robust:
    q: Array
    value: float
    upper: float
    divergence: float
    tilt: float
    iterations: int
    regime: str


def robust_expectation(p: Array, loss: Array, radius: float) -> Robust:
    p = validate(p, loss, radius)
    minimum, maximum = float(np.min(loss)), float(np.max(loss))
    scale = maximum - minimum
    if radius == 0 or scale == 0:
        value = float(p @ loss)
        return Robust(p.copy(), value, value, 0.0, 0.0, 0, "nominal" if radius == 0 else "constant")
    top = loss == maximum
    critical = -np.log(float(p[top].sum()))
    if radius >= critical:
        q = np.where(top, p, 0.0) / p[top].sum()
        return Robust(q, maximum, maximum, kl(q, p), 0.0, 0, "saturated")
    x = (loss - maximum) / scale
    logp = np.log(p)

    def tilted(theta: float) -> tuple[Array, float, float]:
        logits = logp + theta * x
        logz = float(logsumexp(logits))
        q = np.asarray(np.exp(logits - logz), dtype=np.float64)
        # x <= 0 avoids exponential overflow at large theta.
        return q, kl(q, p), logz

    low, high = 0.0, 1.0
    iterations = 0
    while tilted(high)[1] < radius:
        high *= 2
        iterations += 1
        if high > 1e12:
            raise ArithmeticError("cannot bracket KL tilt within the MVP numerical budget")
    for _ in range(100):
        mid = (low + high) / 2
        if tilted(mid)[1] <= radius:
            low = mid
        else:
            high = mid
        iterations += 1
        if high - low <= 1e-12 * max(1.0, high):
            break
    if low == 0:
        raise ArithmeticError("positive tilt unresolved at this radius")
    q, divergence, logz = tilted(low)
    value = float(q @ loss)
    upper = min(maximum, maximum + scale * (radius + logz) / low)
    if not np.isfinite([value, upper, divergence]).all():
        raise ArithmeticError("nonfinite robust result")
    return Robust(q, value, float(upper), divergence, low, iterations, "interior")


def mean_variance_approximation(p: Array, loss: Array, radius: float) -> float:
    p = validate(p, loss, radius)
    mean = float(p @ loss)
    variance = float(p @ ((loss - mean) ** 2))
    return mean + float(np.sqrt(2 * radius * variance))
