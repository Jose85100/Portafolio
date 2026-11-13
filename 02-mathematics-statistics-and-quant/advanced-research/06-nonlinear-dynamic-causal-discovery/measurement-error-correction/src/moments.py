"""Classical measurement-error moment correction with explicit abstention."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]


@dataclass(frozen=True)
class Estimate:
    slope: float | None
    status: str
    condition: float | None


def correct_covariance(
    covariance: Array, noise_variance: float, max_condition: float = 100.0
) -> Estimate:
    """Use covariance of observed(X,W,Y); requires W=Z+v, v independent, Var(v) known.

    Input is assumed to be a valid covariance. The acceptance gate certifies only
    the corrected regressor matrix, not the truth of the measurement model.
    """
    s = np.asarray(covariance, dtype=float)
    if (
        s.shape != (3, 3)
        or not np.isfinite(s).all()
        or not np.allclose(s, s.T, rtol=1e-12, atol=1e-12)
    ):
        raise ValueError("Finite symmetric covariance in(X,W,Y) order required")
    if (
        not np.isfinite(noise_variance)
        or noise_variance < 0
        or not np.isfinite(max_condition)
        or max_condition <= 1
    ):
        raise ValueError("Nonnegative variance and condition cap>1 required")
    c = s[:2, :2].copy()
    c[1, 1] -= noise_variance
    if np.any(np.diag(c) <= 0):
        return Estimate(None, "nonpositive_signal_variance", None)
    scale = np.sqrt(np.diag(c))
    correlation = c / np.outer(scale, scale)
    eigen = np.linalg.eigvalsh(correlation)
    if eigen[0] <= 0:
        return Estimate(None, "nonpositive_moment_matrix", None)
    condition = float(eigen[-1] / eigen[0])
    if condition > max_condition:
        return Estimate(None, "ill_conditioned", condition)
    normalized_rhs = s[:2, 2] / scale
    coefficients = np.linalg.solve(correlation, normalized_rhs) / scale
    return Estimate(float(coefficients[0]), "accepted", condition)


def estimate(
    x: Array,
    proxy: Array,
    y: Array,
    noise_variance: float,
    max_condition: float = 100.0,
) -> Estimate:
    """Centered sample covariance; emits no confidence interval or p value."""
    vectors = [np.asarray(v, dtype=float) for v in (x, proxy, y)]
    if (
        any(v.ndim != 1 for v in vectors)
        or len({len(v) for v in vectors}) != 1
        or len(vectors[0]) < 4
    ):
        raise ValueError("Three matching vectors with at least four rows required")
    if not all(np.isfinite(v).all() for v in vectors):
        raise ValueError("Finite samples required")
    return correct_covariance(
        np.cov(np.vstack(vectors), ddof=1), noise_variance, max_condition
    )


def generate(n: int, effect: float, seed: int) -> tuple[Array, Array, Array, Array]:
    """IID aligned SCM from the26October design, true proxy-noise variance1."""
    if n < 4 or not np.isfinite(effect):
        raise ValueError("n>=4 and finite effect required")
    rng = np.random.default_rng(seed)
    z = rng.normal(size=n)
    x = 0.8 * z + rng.normal(0, 0.5, n)
    y = effect * x + 0.8 * z + rng.normal(0, 0.5, n)
    proxy = z + rng.normal(size=n)
    return x, proxy, y, z


def population_covariance(effect: float, true_noise_variance: float = 1.0) -> Array:
    return np.array(
        [
            [0.89, 0.8, effect * 0.89 + 0.64],
            [0.8, 1 + true_noise_variance, effect * 0.8 + 0.8],
            [
                effect * 0.89 + 0.64,
                effect * 0.8 + 0.8,
                effect**2 * 0.89 + 2 * effect * 0.64 + 0.89,
            ],
        ]
    )
