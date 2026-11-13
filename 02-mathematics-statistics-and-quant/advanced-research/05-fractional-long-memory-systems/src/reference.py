"""Independent 80-digit binomial/Gamma oracles, not a float recurrence replay."""

import mpmath as mp
import numpy as np

from src.fractional import Array, validate_length, validate_order


def prefix_gamma(d: float, m: int) -> float:
    """r_m=Gamma(m+1-d)/(Gamma(1-d) Gamma(m+1))=sum_{k=0}^m w_k."""
    validate_order(d)
    validate_length(m + 1)
    with mp.workdps(80):
        order = mp.mpf(d)
        return float(mp.gamma(m + 1 - order) / (mp.gamma(1 - order) * mp.gamma(m + 1)))


def oracle_filter(x: Array, d: float) -> Array:
    """Short-series reference from binomial special functions and mp.fsum."""
    validate_order(d)
    value = np.asarray(x, dtype=np.float64)
    if value.ndim != 1 or value.size < 1 or value.size > 256 or not np.isfinite(value).all():
        raise ValueError("oracle supports finite 1D series of length 1..256")
    with mp.workdps(80):
        order = mp.mpf(d)
        coeff = [(-1) ** k * mp.binomial(order, k) for k in range(len(value))]
        inputs = [mp.mpf(float(v)) for v in value]
        return np.array(
            [float(mp.fsum(coeff[k] * inputs[t - k] for k in range(t + 1))) for t in range(len(value))],
            dtype=np.float64,
        )
