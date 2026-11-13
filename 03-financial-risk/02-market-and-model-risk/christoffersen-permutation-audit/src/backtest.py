"""Christoffersen independence statistic and conditional permutation calibration."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.stats import chi2

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]


@dataclass(frozen=True)
class IndependenceResult:
    """Three calibrations of the same first-order Markov LR statistic."""

    statistic: float
    asymptotic_p: float
    permutation_p: float
    randomized_p: float


def _xlogy(count: NDArray[np.float64], probability: NDArray[np.float64]) -> FloatArray:
    """Return count*log(probability), defining 0*log(0)=0."""
    out = np.zeros(np.broadcast_shapes(count.shape, probability.shape), dtype=np.float64)
    np.log(probability, out=out, where=probability > 0.0)
    out *= count
    return out


def _transition_counts(hits: NDArray[np.int_]) -> tuple[IntArray, IntArray, IntArray, IntArray]:
    if hits.ndim != 2 or hits.shape[1] < 2:
        raise ValueError("hits must have shape (replications, n>=2)")
    if not np.all((hits == 0) | (hits == 1)):
        raise ValueError("hits must be binary")
    before, after = hits[:, :-1], hits[:, 1:]
    return (
        np.sum((before == 0) & (after == 0), axis=1),
        np.sum((before == 0) & (after == 1), axis=1),
        np.sum((before == 1) & (after == 0), axis=1),
        np.sum((before == 1) & (after == 1), axis=1),
    )


def lr_independence_batch(hits: NDArray[np.int_]) -> FloatArray:
    """Compute Christoffersen's LR independence statistic row-wise."""
    n00, n01, n10, n11 = (x.astype(np.float64) for x in _transition_counts(hits))
    n0, n1 = n00 + n01, n10 + n11
    total = n0 + n1
    pooled = np.divide(n01 + n11, total, out=np.zeros_like(total), where=total > 0)
    p01 = np.divide(n01, n0, out=np.zeros_like(n0), where=n0 > 0)
    p11 = np.divide(n11, n1, out=np.zeros_like(n1), where=n1 > 0)
    ll_null = _xlogy(n00 + n10, 1.0 - pooled) + _xlogy(n01 + n11, pooled)
    ll_markov = _xlogy(n00, 1.0 - p01) + _xlogy(n01, p01) + _xlogy(n10, 1.0 - p11) + _xlogy(n11, p11)
    return np.maximum(0.0, 2.0 * (ll_markov - ll_null))


def lr_independence(hits: NDArray[np.int_]) -> float:
    """Compute Christoffersen's LR independence statistic for one hit sequence."""
    array = np.asarray(hits, dtype=np.int64)
    if array.ndim != 1:
        raise ValueError("hits must be one-dimensional")
    return float(lr_independence_batch(array[None, :])[0])


def conditional_null(n: int, exceptions: int, replications: int, rng: np.random.Generator) -> FloatArray:
    """Simulate LR statistics after uniformly relocating a fixed number of hits."""
    if n < 2 or not 0 <= exceptions <= n or replications < 1:
        raise ValueError("invalid n, exceptions, or replications")
    if exceptions in (0, n):
        return np.zeros(replications, dtype=np.float64)
    priorities = rng.random((replications, n))
    positions = np.argpartition(priorities, exceptions - 1, axis=1)[:, :exceptions]
    samples = np.zeros((replications, n), dtype=np.int8)
    samples[np.arange(replications)[:, None], positions] = 1
    return lr_independence_batch(samples)


def calibrate(
    statistic: float, null_statistics: FloatArray, tie_uniform: float, *, atol: float = 1e-12
) -> IndependenceResult:
    """Return asymptotic, conservative permutation, and randomized permutation p-values."""
    if not 0.0 <= tie_uniform <= 1.0 or null_statistics.ndim != 1:
        raise ValueError("invalid tie uniform or null sample")
    greater = int(np.sum(null_statistics > statistic + atol))
    equal = int(np.sum(np.isclose(null_statistics, statistic, atol=atol, rtol=0.0)))
    b = null_statistics.size
    conservative = (1.0 + greater + equal) / (b + 1.0)
    randomized = (greater + tie_uniform * (equal + 1.0)) / (b + 1.0)
    return IndependenceResult(
        statistic=statistic,
        asymptotic_p=float(chi2.sf(statistic, df=1)),
        permutation_p=float(min(1.0, conservative)),
        randomized_p=float(min(1.0, randomized)),
    )
