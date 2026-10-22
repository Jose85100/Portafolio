"""Categorical Fisher--Rao geometry on the closed simplex; one observation."""

import math
import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]


def simplex(p: Array) -> Array:
    a = np.asarray(p, dtype=np.float64)
    if a.ndim != 1 or not 2 <= a.size <= 4096 or not np.isfinite(a).all() or np.any(a < 0):
        raise ValueError("need finite nonnegative 1D probabilities, 2..4096 categories")
    if not np.isclose(a.sum(), 1, rtol=0, atol=1e-12):
        raise ValueError("probabilities must sum to one")
    return a / a.sum()


def pair(p: Array, q: Array) -> tuple[Array, Array]:
    a, b = simplex(p), simplex(q)
    if a.shape != b.shape:
        raise ValueError("category supports must have the same shape/order")
    return a, b


def hellinger(p: Array, q: Array) -> float:
    a, b = pair(p, q)
    return float(np.linalg.norm(np.sqrt(a) - np.sqrt(b)) / math.sqrt(2))


def fisher_rao(p: Array, q: Array) -> float:
    """4 asin(chord/2); avoids subtracting a near-one affinity."""
    a, b = pair(p, q)
    chord = float(np.linalg.norm(np.sqrt(a) - np.sqrt(b)))
    return float(4 * np.arcsin(np.clip(chord / 2, 0, 1 / math.sqrt(2))))


def local_fisher(p: Array, q: Array) -> float:
    """Tangent quadratic norm at p, NOT a global distance. Undefined at boundary."""
    a, b = pair(p, q)
    if np.any(a == 0):
        raise ValueError("local Fisher norm requires strictly positive base p")
    return float(np.sqrt(np.sum((b - a) ** 2 / a)))


def geodesic(p: Array, q: Array, t: float) -> Array:
    """Square of spherical linear interpolation of unit square-root embeddings."""
    a, b = pair(p, q)
    if not math.isfinite(t) or not 0 <= t <= 1:
        raise ValueError("t must be finite in [0,1]")
    angle = fisher_rao(a, b) / 2
    if angle < 1e-12:
        root = (1 - t) * np.sqrt(a) + t * np.sqrt(b)
    else:
        root = (np.sin((1 - t) * angle) * np.sqrt(a) + np.sin(t * angle) * np.sqrt(b)) / np.sin(angle)
    result = root**2
    return np.asarray(result / result.sum(), dtype=np.float64)
