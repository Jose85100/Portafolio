"""Finite-dimensional linear Gaussian inference; known isotropic noise/prior."""

from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray
from scipy.linalg import lstsq, qr, solve_triangular

Array = NDArray[np.float64]
METHODS = ("svd", "augmented_qr", "normal_equations")


@dataclass(frozen=True)
class Posterior:
    mean: Array
    covariance: Array


def validate(a: Array, y: Array, sigma: float, tau: float) -> None:
    if a.ndim != 2 or not a.size or a.shape[0] < a.shape[1]:
        raise ValueError("A must be nonempty, tall or square")
    if y.shape != (a.shape[0],) or not np.isfinite(a).all() or not np.isfinite(y).all():
        raise ValueError("finite A and matching one-dimensional y required")
    if not np.isfinite([sigma, tau]).all() or min(sigma, tau) < 1e-14 or max(sigma, tau) > 1e4:
        raise ValueError("sigma and tau must lie in [1e-14, 1e4]")
    if np.max(np.abs(a)) > 1e4 or np.max(np.abs(y)) > 1e4:
        raise ValueError("this MVP restricts absolute A/y entries to <= 1e4")


def posterior(a: Array, y: Array, sigma: float, tau: float = 1.0, method: str = "svd") -> Posterior:
    """Posterior for theta~N(0,tau^2 I), y|theta~N(A theta,sigma^2 I)."""
    validate(a, y, sigma, tau)
    d = a.shape[1]
    regularizer = sigma / tau
    if method == "svd":
        u, singular, vt = np.linalg.svd(a, full_matrices=False)
        denom = np.hypot(singular, regularizer)
        # Do not square the singular values in a normal-equations matrix.
        mean = vt.T @ ((singular / denom) * ((u.T @ y) / denom))
        variances = (sigma / denom) ** 2
        covariance = (vt.T * variances) @ vt
    elif method == "augmented_qr":
        augmented = np.vstack((a, regularizer * np.eye(d)))
        target = np.concatenate((y, np.zeros(d)))
        mean = lstsq(augmented, target, cond=0.0, lapack_driver="gelsy")[0]
        _, r, piv = qr(augmented, mode="economic", pivoting=True)
        inverse_r = solve_triangular(r, np.eye(d))
        cov_permuted = (sigma * inverse_r) @ (sigma * inverse_r).T
        covariance = np.empty((d, d))
        covariance[np.ix_(piv, piv)] = cov_permuted
    elif method == "normal_equations":
        precision_scaled = a.T @ a + regularizer**2 * np.eye(d)
        mean = np.linalg.solve(precision_scaled, a.T @ y)
        covariance = sigma**2 * np.linalg.solve(precision_scaled, np.eye(d))
    else:
        raise ValueError(f"unknown method {method}")
    return Posterior(np.asarray(mean), np.asarray((covariance + covariance.T) / 2))


def spectral_variances(singular: Array, sigma: float, tau: float) -> Array:
    """Independent scalar expression used in identifiability diagnostics."""
    return np.asarray((sigma / np.hypot(singular, sigma / tau)) ** 2)
