"""Elliptical coexceedance estimators: finite threshold is not asymptotic lambda."""

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.stats import norm, t

Array = NDArray[np.float64]


@dataclass(frozen=True)
class Copula:
    rho: float
    df: float | None = None

    def __post_init__(self) -> None:
        if not math.isfinite(self.rho) or not -0.95 <= self.rho <= 0.95:
            raise ValueError("rho must be finite in [-.95,.95]; singular copulas are excluded")
        if self.df is not None and (not math.isfinite(self.df) or not 2.1 <= self.df <= 100):
            raise ValueError("df must be None (Gaussian) or finite in [2.1,100]")


def validate_q(q: float) -> None:
    if not math.isfinite(q) or not 0.5 <= q <= 0.99999:
        raise ValueError("supported q in [.5,.99999]")


def validate_n(n: int) -> None:
    if not isinstance(n, int) or isinstance(n, bool) or not 2 <= n <= 10000000:
        raise ValueError("n must be an integer in [2,10000000]")


def kendall_tau(model: Copula) -> float:
    """Elliptical Kendall tau is 2/pi asin(rho), regardless of degrees of freedom."""
    return 2 / math.pi * math.asin(model.rho)


def asymptotic_lambda(model: Copula) -> float:
    """Upper-tail dependence coefficient, not a finite-q probability."""
    if model.df is None:
        return 0.0
    a = math.sqrt((model.df + 1) * (1 - model.rho) / (1 + model.rho))
    return float(2 * t.sf(a, model.df + 1))


def threshold(model: Copula, q: float) -> float:
    validate_q(q)
    return float(norm.isf(1 - q) if model.df is None else t.isf(1 - q, model.df))


def conditional_exceedance(model: Copula, x: Array, a: float) -> Array:
    """P(Y>a|X=x) under the known elliptical joint law."""
    value = np.asarray(x, dtype=np.float64)
    if (
        not np.isfinite(value).all()
        or not math.isfinite(a)
        or np.any(np.abs(value) > 1e100)
        or abs(a) > 1e100
    ):
        raise ValueError("conditioning values and threshold must be finite with absolute value <=1e100")
    if model.df is None:
        return np.asarray(norm.sf((a - model.rho * value) / math.sqrt(1 - model.rho**2)))
    scale = np.sqrt((model.df + value**2) * (1 - model.rho**2) / (model.df + 1))
    return np.asarray(t.sf((a - model.rho * value) / scale, model.df + 1))


def sample_latent(model: Copula, n: int, rng: np.random.Generator) -> Array:
    """Shared chi-square scale is essential for the t copula, including rho=0."""
    validate_n(n)
    z = rng.standard_normal((n, 2))
    z[:, 1] = model.rho * z[:, 0] + math.sqrt(1 - model.rho**2) * z[:, 1]
    if model.df is not None:
        z /= np.sqrt(rng.chisquare(model.df, n) / model.df)[:, None]
    return z


def direct(model: Copula, q: float, n: int, rng: np.random.Generator) -> dict[str, float | int | None]:
    """Unbiased finite-q lambda estimator using known P(X>a)=1-q.

    Also report the common random-denominator estimator without treating 0/0 as zero.
    Fixed-denominator estimates can exceed one in finite samples; do not clip.
    """
    a = threshold(model, q)
    z = sample_latent(model, n, rng)
    first = z[:, 0] > a
    joint = int(np.count_nonzero(first & (z[:, 1] > a)))
    marginal = int(np.count_nonzero(first))
    return {
        "estimate": joint / (n * (1 - q)),
        "joint_count": joint,
        "marginal_count": marginal,
        "random_denominator_estimate": joint / marginal if marginal else None,
    }


def conditional_values(model: Copula, q: float, uniforms: Array) -> Array:
    """Sample X conditional on X>a in survival coordinates, then integrate Y.

    Exact endpoint U=0 is supported; U=1 is explicitly rejected, not clipped.
    Using (1-q)*(1-U) avoids subtracting a rounded CDF close to one.
    """
    validate_q(q)
    u = np.asarray(uniforms, dtype=np.float64)
    if u.ndim != 1 or u.size < 1 or not np.isfinite(u).all() or np.any((u < 0) | (u >= 1)):
        raise ValueError("need nonempty 1D uniforms in [0,1)")
    survival = (1 - q) * (1 - u)
    x = norm.isf(survival) if model.df is None else t.isf(survival, model.df)
    return conditional_exceedance(model, np.asarray(x), threshold(model, q))


def conditional(model: Copula, q: float, n: int, rng: np.random.Generator) -> dict[str, float | int | None]:
    validate_n(n)
    values = conditional_values(model, q, rng.random(n))
    return {"estimate": float(np.mean(values)), "sample_se": float(np.std(values, ddof=1) / math.sqrt(n))}
