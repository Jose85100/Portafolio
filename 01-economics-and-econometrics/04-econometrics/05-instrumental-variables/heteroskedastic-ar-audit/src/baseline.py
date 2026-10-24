"""Single-IV inference with intercept and iid homoskedastic Gaussian AR test."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.stats import f

Array = NDArray[np.float64]


def validate(y: Array, x: Array, z: Array) -> tuple[Array, Array, Array]:
    vectors = [np.asarray(a, dtype=float) for a in (y, x, z)]
    if any(a.ndim != 1 for a in vectors):
        raise ValueError("One-dimensional inputs required")
    if len({a.size for a in vectors}) != 1 or vectors[0].size < 4:
        raise ValueError("Equal lengths >=4 required")
    if any(not np.isfinite(a).all() for a in vectors):
        raise ValueError("Finite inputs required")
    yc, xc, zc = (a - a.mean() for a in vectors)
    if float(zc @ zc) <= 0:
        raise ValueError("Instrument must vary")
    return yc, xc, zc


def ar_pvalue(y: Array, x: Array, z: Array, beta_null: float) -> float:
    """F test of slope in y-beta_null*x ~ 1+z; no division by first stage.

    Exact F(1,n-2) null law conditional on z requires Gaussian iid
    homoskedastic structural errors and valid exclusion; relevance may be zero.
    """
    if not np.isfinite(beta_null):
        raise ValueError("Finite null required")
    yc, xc, zc = validate(y, x, z)
    r = yc - beta_null * xc
    explained = float(zc @ r) ** 2 / float(zc @ zc)
    unexplained = float(r @ r) - explained
    tolerance = np.finfo(float).eps * max(1.0, float(r @ r)) * 16
    if unexplained <= tolerance:
        return 1.0 if explained <= tolerance else 0.0
    return float(f.sf(explained / (unexplained / (len(yc) - 2)), 1, len(yc) - 2))
