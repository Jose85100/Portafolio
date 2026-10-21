"""Causal finite fractional differences with explicit lag-memory budgets."""

import math

import numpy as np
from numpy.typing import NDArray
from scipy.signal import fftconvolve

Array = NDArray[np.float64]


def validate_order(d: float) -> None:
    if not math.isfinite(d) or not 0.01 <= d <= 0.99:
        raise ValueError("supported fractional order is finite in [.01,.99]")


def validate_length(n: int) -> None:
    if not isinstance(n, int) or isinstance(n, bool) or not 1 <= n <= 32768:
        raise ValueError("length must be an integer in [1,32768]")


def weights(d: float, n: int) -> Array:
    """w_k=(-1)^k binom(d,k). Index is lag; w0 always equals one."""
    validate_order(d)
    validate_length(n)
    result = np.empty(n, dtype=np.float64)
    result[0] = 1
    for k in range(1, n):
        result[k] = result[k - 1] * (k - 1 - d) / k
    return result


def tail_masses(w: Array) -> Array:
    """Finite horizon: tail[m]=sum_{k=m+1}^{n-1}|w_k|, tail[n-1]=0.

    No renormalization. Backward summation avoids subtracting nearly equal
    gamma ratios near full memory. The returned bound is numerical float64.
    """
    a = np.asarray(w, dtype=np.float64)
    if a.ndim != 1 or a.size < 1 or not np.isfinite(a).all() or a[0] != 1 or np.any(a[1:] > 0):
        raise ValueError("need finite fractional weights with w0=1 and remaining weights <=0")
    result = np.zeros_like(a)
    if a.size > 1:
        result[:-1] = np.cumsum(np.abs(a[:0:-1]))[::-1]
    return result


def budget_memory(w: Array, tolerance: float) -> int:
    """Smallest retained maximum lag m with finite-horizon tail <= tolerance."""
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and nonnegative")
    tails = tail_masses(w)
    return int(np.flatnonzero(tails <= tolerance)[0])


def coefficient_memory(w: Array, epsilon: float) -> int:
    """Audited heuristic: discard the first coefficient |w_k|<=epsilon and all later lags.

    epsilon bounds one discarded coefficient, NOT their accumulated sum.
    """
    if not math.isfinite(epsilon) or epsilon <= 0:
        raise ValueError("coefficient epsilon must be finite and positive")
    tail_masses(w)
    indices = np.flatnonzero(np.abs(w[1:]) <= epsilon)
    return int(indices[0]) if indices.size else len(w) - 1


def apply_filter(x: Array, w: Array, memory: int | None = None, *, method: str = "direct") -> Array:
    """Linear convolution, first n values; unobserved prehistory is exactly zero."""
    series = np.asarray(x, dtype=np.float64)
    kernel = np.asarray(w, dtype=np.float64)
    if series.ndim != 1 or series.size < 1 or not np.isfinite(series).all() or np.max(np.abs(series)) > 1e8:
        raise ValueError("need finite 1D input, sup norm <=1e8")
    validate_length(len(series))
    tail_masses(kernel)
    if len(kernel) != len(series):
        raise ValueError("full weight vector must match input length")
    m = len(kernel) - 1 if memory is None else memory
    if not isinstance(m, int) or isinstance(m, bool) or not 0 <= m < len(kernel):
        raise ValueError("memory is a retained maximum lag in [0,n-1]")
    if method == "direct":
        return np.asarray(np.convolve(series, kernel[: m + 1], mode="full")[: len(series)], dtype=np.float64)
    if method == "fft":
        return np.asarray(fftconvolve(series, kernel[: m + 1], mode="full")[: len(series)])
    raise ValueError("method must be direct or fft; circular convolution is not supported")
