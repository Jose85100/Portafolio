"""Single-IV inference with intercept and iid homoskedastic Gaussian AR test."""

from __future__ import annotations
import numpy as np
from numpy.typing import NDArray
from scipy.stats import f, norm

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


def wald_pvalue(y: Array, x: Array, z: Array, beta_null: float) -> float:
    """Conventional homoskedastic IV normal Wald test, a weak-IV-unsafe baseline."""
    if not np.isfinite(beta_null):
        raise ValueError("Finite null required")
    yc, xc, zc = validate(y, x, z)
    cross = float(zc @ xc)
    if abs(cross) < np.finfo(float).eps:
        return 1.0
    estimate = float(zc @ yc) / cross
    residual = yc - estimate * xc
    variance = float(residual @ residual) / (len(yc) - 2)
    se = np.sqrt(variance * float(zc @ zc) / cross**2)
    return (
        float(2 * norm.sf(abs((estimate - beta_null) / se)))
        if se
        else float(estimate == beta_null)
    )


def first_stage_f(x: Array, z: Array) -> float:
    xc, _, zc = validate(x, x, z)
    if float(xc @ xc) <= 0:
        return 0.0
    explained = float(zc @ xc) ** 2 / float(zc @ zc)
    unexplained = max(0.0, float(xc @ xc) - explained)
    return explained / (unexplained / (len(xc) - 2)) if unexplained else float("inf")


def sample(
    seed: int,
    n: int,
    strength: float,
    rho: float = 0.8,
    exclusion: float = 0.0,
    beta: float = 1.0,
) -> tuple[Array, Array, Array]:
    """x=c/sqrt(n)*z+v; y=beta*x+u+gamma*z; Corr(u,v)=rho."""
    if n < 4 or not -1 < rho < 1:
        raise ValueError("n>=4 and |rho|<1 required")
    rng = np.random.default_rng(seed)
    z, v, noise = rng.normal(size=(3, n))
    u = rho * v + np.sqrt(1 - rho**2) * noise
    x = strength / np.sqrt(n) * z + v
    return beta * x + u + exclusion * z, x, z
