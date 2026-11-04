"""Finite-sample variance inference for a stationary Gaussian AR(1).

The dependence parameter is treated as known externally.  The paired-difference
interval is a Chebyshev interval derived from the exact covariance of squared
Gaussian AR(1) increments; it is deliberately compared with an exact
Prais-Winsten/GLS chi-square interval rather than presented as a new theorem.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from collections.abc import Sequence

import numpy as np
from scipy.stats import chi2


@dataclass(frozen=True)
class VarianceEstimate:
    estimate: float
    low: float | None
    high: float | None
    confidence: float
    observations: int
    method: str
    abstained: bool = False


def _validate(x: Sequence[float], rho: float, confidence: float) -> np.ndarray:
    if not math.isfinite(rho) or not -1.0 < rho < 1.0:
        raise ValueError("rho must be finite and strictly between -1 and 1")
    if not math.isfinite(confidence) or not 0.5 <= confidence < 1.0:
        raise ValueError("confidence must be finite and in [0.5, 1)")
    values = np.asarray(x, dtype=np.float64)
    if values.ndim != 1 or values.size < 3 or not np.isfinite(values).all():
        raise ValueError("need at least three finite one-dimensional observations")
    return values


def pair_variance_coefficient(n: int, rho: float) -> float:
    """Return c such that Var(vhat_pair)=c*v**2 for m=n-1 increments.

    For Z_t=(X_t-X_{t-1})**2/[2(1-rho)],
    Cov(Z_t,Z_{t+h})=v**2*(1-rho)**2*rho**(2(h-1))/2, h>=1.
    """
    if not isinstance(n, int) or n < 3:
        raise ValueError("n must be an integer >= 3")
    if not math.isfinite(rho) or not -1.0 < rho < 1.0:
        raise ValueError("rho must be finite and strictly between -1 and 1")
    m = n - 1
    serial = sum((m - h) * rho ** (2 * (h - 1)) for h in range(1, m))
    return (2.0 * m + 0.5 * (1.0 - rho) ** 2 * 2.0 * serial) / (m * m)


def paired_chebyshev_interval(
    x: Sequence[float], rho: float, confidence: float = 0.9
) -> VarianceEstimate:
    """A conservative, finite-sample interval for stationary Gaussian AR(1).

    Chebyshev is applied to the relative error. If epsilon=sqrt(c/alpha)>=1,
    the multiplicative interval is unbounded above and the function abstains.
    """
    values = _validate(x, rho, confidence)
    alpha = 1.0 - confidence
    increments = np.diff(values)
    estimate = float(np.mean(increments * increments) / (2.0 * (1.0 - rho)))
    coefficient = pair_variance_coefficient(len(values), rho)
    epsilon = math.sqrt(coefficient / alpha)
    if not math.isfinite(estimate) or epsilon >= 1.0:
        return VarianceEstimate(estimate, None, None, confidence, len(values), "paired_chebyshev", True)
    return VarianceEstimate(
        estimate,
        estimate / (1.0 + epsilon),
        estimate / (1.0 - epsilon),
        confidence,
        len(values),
        "paired_chebyshev",
    )


def gls_chisquare_interval(
    x: Sequence[float], rho: float, confidence: float = 0.9
) -> VarianceEstimate:
    """Exact Gaussian interval after known-rho Prais-Winsten whitening.

    The unknown stationary mean is estimated by GLS. The transformed residual
    sum of squares divided by n-1 is chi-square scaled by the marginal variance.
    """
    values = _validate(x, rho, confidence)
    n = len(values)
    root = math.sqrt(1.0 - rho * rho)
    z = np.empty(n, dtype=np.float64)
    h = np.empty(n, dtype=np.float64)
    z[0] = values[0]
    z[1:] = (values[1:] - rho * values[:-1]) / root
    h[0] = 1.0
    h[1:] = (1.0 - rho) / root
    mean_hat = float(np.dot(h, z) / np.dot(h, h))
    residual = z - h * mean_hat
    df = n - 1
    estimate = float(np.dot(residual, residual) / df)
    alpha = 1.0 - confidence
    low = df * estimate / float(chi2.ppf(1.0 - alpha / 2.0, df))
    high = df * estimate / float(chi2.ppf(alpha / 2.0, df))
    return VarianceEstimate(estimate, low, high, confidence, n, "gls_chisquare")


def iid_chisquare_interval(
    x: Sequence[float], confidence: float = 0.9
) -> VarianceEstimate:
    """Mis-specified iid chi-square interval, retained as a diagnostic baseline."""
    if not math.isfinite(confidence) or not 0.5 <= confidence < 1.0:
        raise ValueError("confidence must be finite and in [0.5, 1)")
    values = np.asarray(x, dtype=np.float64)
    if values.ndim != 1 or values.size < 3 or not np.isfinite(values).all():
        raise ValueError("need at least three finite one-dimensional observations")
    n = len(values)
    estimate = float(np.var(values, ddof=1))
    df = n - 1
    alpha = 1.0 - confidence
    low = df * estimate / float(chi2.ppf(1.0 - alpha / 2.0, df))
    high = df * estimate / float(chi2.ppf(alpha / 2.0, df))
    return VarianceEstimate(estimate, low, high, confidence, n, "iid_chisquare")
