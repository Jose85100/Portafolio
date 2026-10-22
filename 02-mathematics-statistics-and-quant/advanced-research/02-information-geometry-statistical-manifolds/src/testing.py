"""Exchangeable two-sample categorical tests with shared random label partitions."""

import math
import numpy as np
from numpy.typing import NDArray
from scipy.stats import chi2

Array = NDArray[np.float64]


def counts_pair(a: Array, b: Array) -> tuple[Array, Array]:
    x, y = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if x.ndim != 1 or not 2 <= x.size <= 4096 or x.shape != y.shape:
        raise ValueError("need same categorical count vectors")
    if (
        not np.isfinite(x).all()
        or not np.isfinite(y).all()
        or np.any(x < 0)
        or np.any(y < 0)
        or np.any(x != np.floor(x))
        or np.any(y != np.floor(y))
    ):
        raise ValueError("counts must be finite nonnegative integers")
    if not 1 <= x.sum() <= 100000 or not 1 <= y.sum() <= 100000:
        raise ValueError("sample sizes must be in [1,100000]")
    return x, y


def statistics(a: Array, b: Array) -> dict[str, Array]:
    """Vectorized rows of counts. Internal: validated observed or generated counts."""
    x, y = np.atleast_2d(a), np.atleast_2d(b)
    n, m = x.sum(axis=1, keepdims=True), y.sum(axis=1, keepdims=True)
    chord = np.linalg.norm(np.sqrt(x / n) - np.sqrt(y / m), axis=1)
    total = x + y
    ex = n * total / (n + m)
    ey = m * total / (n + m)
    pearson = np.sum(
        np.divide((x - ex) ** 2, ex, out=np.zeros_like(ex), where=ex > 0)
        + np.divide((y - ey) ** 2, ey, out=np.zeros_like(ey), where=ey > 0),
        axis=1,
    )
    return {
        "fr": 4 * np.arcsin(np.clip(chord / 2, 0, 1 / math.sqrt(2))),
        "hellinger": chord / math.sqrt(2),
        "pearson": pearson,
    }


def monte_carlo_p(observed: float, null: Array) -> float:
    values = np.asarray(null, dtype=float)
    if values.ndim != 1 or values.size < 1 or not np.isfinite(values).all() or not math.isfinite(observed):
        raise ValueError("need finite statistic and nonempty finite null")
    # Conservative tolerance for floating-point ties, matching SciPy convention in spirit.
    tol = 1e-12 * max(1, abs(observed))
    return float((1 + np.count_nonzero(values >= observed - tol)) / (values.size + 1))


def permutation_test(a: Array, b: Array, permutations: int, seed: int) -> dict[str, float]:
    x, y = counts_pair(a, b)
    if not isinstance(permutations, int) or isinstance(permutations, bool) or not 1 <= permutations <= 10000:
        raise ValueError("permutations must be integer in [1,10000]")
    rng = np.random.default_rng(seed)
    pooled = (x + y).astype(np.int64)
    # Uniform fixed-size label partitions induce the multivariate hypergeometric law.
    xp = rng.multivariate_hypergeometric(pooled, int(x.sum()), size=permutations)
    yp = pooled - xp
    obs = statistics(x, y)
    null = statistics(xp.astype(float), yp.astype(float))
    result = {f"p_{key}": monte_carlo_p(float(obs[key][0]), null[key]) for key in obs}
    active = int(np.count_nonzero(pooled))
    result["p_pearson_asymptotic"] = float(chi2.sf(obs["pearson"][0], active - 1)) if active > 1 else 1.0
    result["fr"] = float(obs["fr"][0])
    result["hellinger"] = float(obs["hellinger"][0])
    result["pearson"] = float(obs["pearson"][0])
    return result
