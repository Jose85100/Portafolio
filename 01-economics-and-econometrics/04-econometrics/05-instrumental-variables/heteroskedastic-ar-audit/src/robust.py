"""Heteroskedasticity-consistent reduced-form AR Wald test, asymptotic chi-square."""

from __future__ import annotations

import numpy as np
from scipy.stats import chi2

from src.baseline import Array, validate


def robust_ar(
    y: Array, x: Array, z: Array, beta_null: float, kind: str = "HC3"
) -> float:
    """Test slope=0 in r=y-beta_null*x on [1,z], HC1/HC3 covariance.

    This retains weak-relevance robustness under valid exclusion but only
    asymptotic calibration for independent heteroskedastic observations.
    It is NOT the exact finite-sample Gaussian F test.
    """
    if not np.isfinite(beta_null) or kind not in ("HC1", "HC3"):
        raise ValueError("Finite null and HC1/HC3 required")
    yc, xc, zc = validate(y, x, z)
    r = yc - beta_null * xc
    n = len(yc)
    szz = float(zc @ zc)
    slope = float(zc @ r) / szz
    residual = r - slope * zc
    leverage = 1 / n + zc**2 / szz
    if np.max(leverage) >= 1 - 1e-12:
        raise ValueError("Leverage one: heteroskedastic covariance unidentified")
    weighted = residual**2
    if kind == "HC1":
        weighted = weighted * n / (n - 2)
    else:
        weighted = weighted / (1 - leverage) ** 2
    variance = float((zc**2) @ weighted) / szz**2
    if variance <= np.finfo(float).tiny:
        return float(abs(slope) < np.finfo(float).eps)
    return float(chi2.sf(slope**2 / variance, 1))


def sample(
    seed: int, n: int, hetero: bool, c: float = 1.0, gamma: float = 0.0
) -> tuple[Array, Array, Array]:
    """Synthetic IID sample with E[u|z]=0 unless direct effect gamma is nonzero."""
    if n < 4:
        raise ValueError("n>=4 required")
    rng = np.random.default_rng(seed)
    z, v, e = rng.normal(size=(3, n))
    scale = np.sqrt((0.1 + z * z) / 1.1) if hetero else np.ones(n)
    u = scale * (0.8 * v + 0.6 * e)
    x = c * z / np.sqrt(n) + v
    return x + u + gamma * z, x, z
