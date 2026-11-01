"""Gaussian confidence interval of variance, with an explicit bounded audit domain."""

from __future__ import annotations
from dataclasses import dataclass
import math
from collections.abc import Sequence
import numpy as np
from scipy.stats import chi2


@dataclass(frozen=True)
class VarianceInterval:
    sample_variance: float
    low: float
    high: float
    confidence: float
    size: int


def gaussian_variance_interval(
    samples: Sequence[float], confidence: float = 0.9
) -> VarianceInterval | None:
    """Exact only for independent identically distributed Gaussian observations.

    Intersection with [0,16] assumes the true variance lies in that audit domain.
    None means no intersection, never a silently forced point estimate.
    A constant sample maps to [0,0]; it has probability zero for positive Gaussian variance.
    """
    if not math.isfinite(confidence) or not 0.5 <= confidence <= 0.99:
        raise ValueError("Require .5<=confidence<=.99")
    x = np.asarray(samples, dtype=float)
    if x.ndim != 1 or len(x) < 2 or not np.isfinite(x).all():
        raise ValueError("Require at least two finite observations in one dimension")
    with np.errstate(over="ignore", invalid="ignore"):
        sample_variance = float(np.var(x, ddof=1))
    if not math.isfinite(sample_variance):
        raise ValueError("Variance overflow; rescale observations explicitly")
    df = len(x) - 1
    tail = (1 - confidence) / 2
    low = float(df * sample_variance / chi2.ppf(1 - tail, df))
    high = float(df * sample_variance / chi2.ppf(tail, df))
    if low > 16:
        return None
    return VarianceInterval(sample_variance, low, min(high, 16.0), confidence, len(x))


def wilson_interval(successes: int, total: int) -> tuple[float, float]:
    """95% Wilson interval for independent Bernoulli simulation coverage indicators."""
    if (
        not isinstance(successes, int)
        or not isinstance(total, int)
        or not 0 <= successes <= total
        or total <= 0
    ):
        raise ValueError("Require integer 0<=successes<=total and total>0")
    z = 1.959963984540054
    phat = successes / total
    denominator = 1 + z * z / total
    centre = (phat + z * z / (2 * total)) / denominator
    half = (
        z
        * math.sqrt(phat * (1 - phat) / total + z * z / (4 * total * total))
        / denominator
    )
    return max(0.0, centre - half), min(1.0, centre + half)
