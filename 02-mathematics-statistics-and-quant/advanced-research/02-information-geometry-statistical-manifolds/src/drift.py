"""Calibrated continuous two-sample drift detection with an explicit Gaussian projection."""

import math
from dataclasses import dataclass
import numpy as np
from scipy.stats import ks_2samp, wasserstein_distance, binom
from src.geometry import Array


def sample(x: Array) -> Array:
    a = np.asarray(x, dtype=np.float64)
    if a.ndim != 1 or not 4 <= a.size <= 10000 or not np.isfinite(a).all() or np.max(np.abs(a)) > 1e8:
        raise ValueError("need 4..10000 finite observations bounded by 1e8")
    if np.std(a) < 1e-12:
        raise ValueError("degenerate sample: positive scale required, no silent regularization")
    return a


def normal_fr(mu: float, sigma: float, other_mu: float, other_sigma: float) -> float:
    """Exact N(mu,sigma²) Fisher--Rao distance; stable acosh(1+z) identity."""
    if (
        not all(math.isfinite(v) for v in [mu, sigma, other_mu, other_sigma])
        or min(sigma, other_sigma) < 1e-12
        or max(sigma, other_sigma) > 1e8
        or max(abs(mu), abs(other_mu)) > 1e8
    ):
        raise ValueError("finite means bounded by 1e8; scales in [1e-12,1e8]")
    z = ((mu - other_mu) ** 2 + 2 * (sigma - other_sigma) ** 2) / (4 * sigma * other_sigma)
    return float(2 * math.sqrt(2) * math.asinh(math.sqrt(z / 2)))


def scores(reference: Array, current: Array) -> Array:
    a, b = sample(reference), sample(current)
    if a.size != b.size:
        raise ValueError("reference and current must have matched sizes")
    ma, sa = float(np.mean(a)), float(np.std(a))
    mb, sb = float(np.mean(b)), float(np.std(b))
    return np.array(
        [
            normal_fr(ma, sa, mb, sb),
            ks_2samp(a, b, method="asymp").statistic,
            wasserstein_distance(a, b) / sa,
        ],
        dtype=np.float64,
    )


def rank_threshold(values: Array, alpha: float, delta: float | None = None) -> Array:
    a = np.asarray(values, dtype=float)
    if (
        a.ndim != 2
        or a.shape[0] < 1
        or a.shape[1] != 3
        or not np.isfinite(a).all()
        or not math.isfinite(alpha)
        or not 0 < alpha < 1
    ):
        raise ValueError("finite B x 3 calibration scores and alpha in (0,1) required")
    rank = math.ceil((len(a) + 1) * (1 - alpha))
    if delta is not None:
        if not math.isfinite(delta) or not 0 < delta < 1:
            raise ValueError("delta must lie in (0,1)")
        # One-sided tolerance bound, Bonferroni across the three score functions.
        rank = int(binom.ppf(1 - delta / 3, len(a), 1 - alpha)) + 1
    if rank > len(a):
        return np.full(3, np.inf)
    return np.asarray(np.sort(a, axis=0)[rank - 1], dtype=np.float64)


@dataclass(frozen=True)
class Detector:
    reference: Array
    thresholds: Array

    def predict(self, current: Array) -> tuple[Array, Array]:
        values = scores(self.reference, current)
        return values, np.asarray(values > self.thresholds, dtype=bool)


def calibrate(reference: Array, windows: Array, alpha: float = 0.05, delta: float | None = 0.05) -> Detector:
    a = sample(reference).copy()
    w = np.asarray(windows, dtype=float)
    if w.ndim != 2 or w.shape[1] != a.size or not 1 <= len(w) <= 10000:
        raise ValueError("need B x n independent baseline windows, same size as reference")
    values = np.stack([scores(a, row) for row in w])
    a.setflags(write=False)
    thresholds = rank_threshold(values, alpha, delta)
    thresholds.setflags(write=False)
    return Detector(a, thresholds)
