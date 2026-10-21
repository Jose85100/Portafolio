"""Numerical certificate for scale-gauge non-identifiability."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class Certificate:
    """Spectral diagnosis of a Jacobian/Fisher matrix."""

    eigenvalues: FloatArray
    nullity: int
    rank: int
    tolerance: float
    condition_identifiable: float


def _vector(x: FloatArray, name: str, *, allow_zero: bool = False) -> FloatArray:
    value = np.asarray(x, dtype=np.float64)
    if value.ndim != 1 or value.size < 1 or not np.all(np.isfinite(value)):
        raise ValueError(f"{name} must be a non-empty finite vector")
    if not allow_zero and np.linalg.norm(value) <= np.finfo(float).tiny:
        raise ValueError(f"{name} must be nonzero")
    return value


def mean_matrix(u: FloatArray, v: FloatArray) -> FloatArray:
    """Mean map mu(u,v)=u v^T."""
    left = _vector(u, "u", allow_zero=True)
    right = _vector(v, "v", allow_zero=True)
    return np.asarray(np.outer(left, right), dtype=np.float64)


def analytic_jacobian(u: FloatArray, v: FloatArray) -> FloatArray:
    """Jacobian of vec(mu), using row-major vectorization."""
    left = _vector(u, "u", allow_zero=True)
    right = _vector(v, "v", allow_zero=True)
    m, n = left.size, right.size
    jacobian = np.zeros((m * n, m + n), dtype=np.float64)
    for i in range(m):
        jacobian[i * n : (i + 1) * n, i] = right
        jacobian[i * n : (i + 1) * n, m:] = np.eye(n) * left[i]
    return jacobian


def finite_difference_jacobian(u: FloatArray, v: FloatArray, step: float = 1e-6) -> FloatArray:
    """Central-difference baseline for the same mean map."""
    left = _vector(u, "u", allow_zero=True)
    right = _vector(v, "v", allow_zero=True)
    if not np.isfinite(step) or step <= 0:
        raise ValueError("step must be positive and finite")
    theta = np.concatenate([left, right])
    result = np.empty((left.size * right.size, theta.size), dtype=np.float64)
    for column in range(theta.size):
        plus = theta.copy()
        minus = theta.copy()
        plus[column] += step
        minus[column] -= step
        result[:, column] = (
            mean_matrix(plus[: left.size], plus[left.size :]).ravel()
            - mean_matrix(minus[: left.size], minus[left.size :]).ravel()
        ) / (2.0 * step)
    return result


def fisher_information(jacobian: FloatArray, noise_std: float) -> FloatArray:
    """Gaussian Fisher information J^T J / sigma^2."""
    matrix = np.asarray(jacobian, dtype=np.float64)
    if matrix.ndim != 2 or not np.all(np.isfinite(matrix)):
        raise ValueError("jacobian must be a finite matrix")
    if not np.isfinite(noise_std) or noise_std <= 0:
        raise ValueError("noise_std must be positive and finite")
    return (matrix.T @ matrix) / noise_std**2


def spectral_certificate(fisher: FloatArray, rtol: float | None = None) -> Certificate:
    """Count numerical null directions and condition the identifiable subspace."""
    matrix = np.asarray(fisher, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or matrix.size == 0:
        raise ValueError("fisher must be a non-empty square matrix")
    if not np.all(np.isfinite(matrix)) or not np.allclose(matrix, matrix.T, atol=1e-12):
        raise ValueError("fisher must be finite and symmetric")
    values = np.linalg.eigvalsh((matrix + matrix.T) / 2.0)
    maximum = float(max(abs(values[-1]), 1.0))
    relative = matrix.shape[0] * np.finfo(float).eps if rtol is None else rtol
    if not np.isfinite(relative) or relative <= 0:
        raise ValueError("rtol must be positive and finite")
    tolerance = float(relative * maximum)
    positive = values[values > tolerance]
    nullity = int(values.size - positive.size)
    condition = float(positive[-1] / positive[0]) if positive.size else float("inf")
    return Certificate(
        np.asarray(values, dtype=np.float64), nullity, int(positive.size), tolerance, condition
    )


def gauge_tangent(u: FloatArray, v: FloatArray) -> FloatArray:
    """Tangent at c=1 to (c u, v/c)."""
    return np.concatenate([_vector(u, "u"), -_vector(v, "v")])


def canonicalize(u: FloatArray, v: FloatArray) -> tuple[FloatArray, FloatArray]:
    """Choose the balanced, sign-oriented representative of a rank-one orbit."""
    left = _vector(u, "u")
    right = _vector(v, "v")
    product = np.outer(left, right)
    p, singular, qt = np.linalg.svd(product, full_matrices=False)
    root = float(np.sqrt(singular[0]))
    fixed_left = p[:, 0] * root
    fixed_right = qt[0, :] * root
    index = int(np.argmax(np.abs(fixed_left)))
    if fixed_left[index] < 0:
        fixed_left = -fixed_left
        fixed_right = -fixed_right
    return fixed_left.astype(np.float64), fixed_right.astype(np.float64)


def best_rank_one(data: FloatArray) -> tuple[FloatArray, FloatArray]:
    """Balanced Eckart--Young rank-one least-squares estimate."""
    matrix = np.asarray(data, dtype=np.float64)
    if matrix.ndim != 2 or min(matrix.shape) < 1 or not np.all(np.isfinite(matrix)):
        raise ValueError("data must be a non-empty finite matrix")
    p, singular, qt = np.linalg.svd(matrix, full_matrices=False)
    if singular[0] <= np.finfo(float).tiny:
        raise ValueError("rank-one estimate is degenerate")
    root = float(np.sqrt(singular[0]))
    return canonicalize(p[:, 0] * root, qt[0, :] * root)
