"""Known quantile-integral ES; losses are positive costs, weights are probabilities."""

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class TailResult:
    var: float
    es: float
    tail_mass: float


def distribution(losses: ArrayLike, weights: ArrayLike | None = None) -> tuple[FloatArray, FloatArray]:
    """Validate and normalize nonnegative weights; exclude zero-probability scenarios."""
    x = np.asarray(losses, dtype=np.float64)
    if x.ndim != 1 or x.size == 0 or not np.all(np.isfinite(x)):
        raise ValueError("losses must be a nonempty finite vector")
    p = np.ones(x.size, dtype=np.float64) if weights is None else np.asarray(weights, dtype=np.float64)
    if p.shape != x.shape or not np.all(np.isfinite(p)) or np.any(p < 0) or not np.any(p > 0):
        raise ValueError("weights must match losses, be finite, nonnegative, and have positive mass")
    keep = p > 0
    x, p = x[keep], p[keep]
    # Scale first to avoid overflow when unnormalized weights are very large.
    p = p / np.max(p)
    p = p / math.fsum(p.tolist())
    return x, p


def confidence(alpha: float) -> float:
    if not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be finite and strictly inside (0,1)")
    return 1.0 - alpha


def weighted_tail(losses: ArrayLike, alpha: float = 0.975, weights: ArrayLike | None = None) -> TailResult:
    """Integrate the upper 1-alpha probability mass, splitting the boundary atom.

    VaR is the left inverse of the CDF, not a linearly interpolated sample quantile.
    Complexity O(n log n), memory O(n). Does not estimate population uncertainty.
    """
    mass = confidence(alpha)
    x, p = distribution(losses, weights)
    order = np.argsort(x, kind="stable")
    ascending, prob = x[order], p[order]
    cdf = np.cumsum(prob)
    cdf[-1] = 1.0
    index = min(int(np.searchsorted(cdf, alpha, side="left")), len(x) - 1)
    descending, reverse_prob = ascending[::-1], prob[::-1]
    before = np.concatenate((np.array([0.0]), np.cumsum(reverse_prob[:-1])))
    used = np.minimum(reverse_prob, np.maximum(mass - before, 0.0))
    fractions = used / mass
    scale = max(float(np.max(np.abs(descending))), 1.0)
    es = scale * math.fsum((fractions * (descending / scale)).tolist())
    if not math.isfinite(es):
        raise ValueError("ES overflow")
    return TailResult(float(ascending[index]), es, math.fsum(used.tolist()))


def equal_mass_reference(losses: ArrayLike, alpha: float = 0.975) -> float:
    """Independent equal-probability order-statistic implementation (repo convention)."""
    x, _ = distribution(losses)
    mass = confidence(alpha) * x.size
    x = np.sort(x)[::-1]
    whole = int(math.floor(mass))
    numerator = math.fsum(x[:whole].tolist())
    if whole < x.size:
        numerator += (mass - whole) * float(x[whole])
    return numerator / mass
