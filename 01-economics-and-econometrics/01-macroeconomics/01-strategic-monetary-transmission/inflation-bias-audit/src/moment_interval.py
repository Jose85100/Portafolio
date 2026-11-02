"""Finite-sample variance interval under an externally justified kurtosis bound."""

from __future__ import annotations
from collections.abc import Sequence
from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class PairInterval:
    estimate: float
    low: float
    high: float
    radius: float
    pairs: int


def bounded_kurtosis_interval(
    samples: Sequence[float], kurtosis_bound: float = 9.0, confidence: float = 0.9
) -> PairInterval | None:
    """Coverage >= confidence if IID, Pearson kurtosis <= bound and 0<=v<=16.

    Disjoint adjacent pairs remove an unknown mean. An odd last observation is
    ignored. Pair order is part of the data contract. None denotes empty audit
    domain intersection. Bound is external, never a fitted sample kurtosis.
    """
    if not math.isfinite(kurtosis_bound) or not 1 <= kurtosis_bound <= 100:
        raise ValueError("Require finite Pearson kurtosis bound in [1,100]")
    if not math.isfinite(confidence) or not 0.5 <= confidence <= 0.99:
        raise ValueError("Require confidence in [.5,.99]")
    x = np.asarray(samples, dtype=float)
    if x.ndim != 1 or len(x) < 2 or not np.isfinite(x).all():
        raise ValueError("Require finite one-dimensional sample, n>=2")
    m = len(x) // 2
    with np.errstate(over="ignore", invalid="ignore"):
        differences = x[: 2 * m : 2] - x[1 : 2 * m : 2]
        estimate = float(np.mean(differences**2 / 2))
    if not math.isfinite(estimate):
        raise ValueError("Pair squares overflow; explicitly rescale observations")
    radius = math.sqrt((kurtosis_bound + 1) / (2 * m * (1 - confidence)))
    low = estimate / (1 + radius)
    if low > 16:
        return None
    high = 16.0 if radius >= 1 else min(16.0, estimate / (1 - radius))
    return PairInterval(estimate, low, high, radius, m)
