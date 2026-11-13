"""Small, typed simulation study of rolling conformal intervals."""
from __future__ import annotations

from dataclasses import dataclass
from statistics import NormalDist
from typing import Iterable
import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class Coverage:
    covered: int
    count: int

    @property
    def rate(self) -> float:
        return self.covered / self.count if self.count else float("nan")


def conformal_quantile(scores: Iterable[float], alpha: float) -> float:
    """Finite-sample split-conformal order statistic (ceil((n+1)(1-a)))."""
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    values = np.asarray(list(scores), dtype=float)
    if values.ndim != 1 or values.size == 0 or not np.all(np.isfinite(values)):
        raise ValueError("scores must be a nonempty finite vector")
    k = min(values.size, int(np.ceil((values.size + 1) * (1.0 - alpha))))
    return float(np.partition(values, k - 1)[k - 1])


def rolling_interval(calibration: Iterable[float], center: float, alpha: float) -> tuple[float, float]:
    q = conformal_quantile(calibration, alpha)
    return center - q, center + q


def coverage(truth: FloatArray, lower: FloatArray, upper: FloatArray) -> Coverage:
    if not (truth.shape == lower.shape == upper.shape) or truth.size == 0:
        raise ValueError("truth and bounds must have the same nonempty shape")
    if np.any(lower > upper):
        raise ValueError("lower bound exceeds upper bound")
    return Coverage(int(np.count_nonzero((truth >= lower) & (truth <= upper))), int(truth.size))


def simulate(seed: int, n: int = 3000, change: int = 1500, sigma_after: float = 2.0) -> FloatArray:
    """Zero-mean independent Gaussian innovations, with optional scale break."""
    if n < 2 or not 0 <= change <= n or sigma_after <= 0:
        raise ValueError("invalid simulation dimensions or scale")
    rng = np.random.default_rng(seed)
    scale = np.ones(n)
    scale[change:] = sigma_after
    return rng.normal(size=n) * scale


def evaluate(series: FloatArray, alpha: float = .1, window: int = 200, oracle_scale: FloatArray | None = None) -> dict[str, float]:
    """Compare fixed initial calibration with adaptive trailing-window calibration."""
    if series.ndim != 1 or window < 2 or series.size <= window:
        raise ValueError("need 1-D series longer than calibration window >=2")
    scores = np.abs(series)
    lo_fixed = np.empty(series.size - window)
    hi_fixed = np.empty_like(lo_fixed)
    lo_roll = np.empty_like(lo_fixed)
    hi_roll = np.empty_like(lo_fixed)
    truth = series[window:]
    scales = np.ones(series.size) if oracle_scale is None else oracle_scale
    if scales.shape != series.shape or np.any(scales <= 0) or not np.all(np.isfinite(scales)):
        raise ValueError("oracle_scale must be positive, finite, and match series shape")
    fixed_q = conformal_quantile(scores[:window], alpha)
    for j, i in enumerate(range(window, series.size)):
        q = conformal_quantile(scores[i-window:i], alpha)
        lo_fixed[j], hi_fixed[j] = -fixed_q, fixed_q
        lo_roll[j], hi_roll[j] = -q, q
    split = max(0, (series.size // 2) - window)
    oracle_q = NormalDist().inv_cdf(1.0-alpha/2) * scales[window:]
    oracle_cov = coverage(truth, -oracle_q, oracle_q)
    return {
        "fixed_coverage": coverage(truth, lo_fixed, hi_fixed).rate,
        "rolling_coverage": coverage(truth, lo_roll, hi_roll).rate,
        "fixed_mean_width": float(np.mean(hi_fixed-lo_fixed)),
        "rolling_mean_width": float(np.mean(hi_roll-lo_roll)),
        "fixed_postbreak_coverage": coverage(truth[split:], lo_fixed[split:], hi_fixed[split:]).rate,
        "rolling_postbreak_coverage": coverage(truth[split:], lo_roll[split:], hi_roll[split:]).rate,
        "oracle_coverage": oracle_cov.rate,
        "oracle_mean_width": float(np.mean(2*oracle_q)),
        "oracle_postbreak_coverage": coverage(truth[split:], -oracle_q[split:], oracle_q[split:]).rate,
    }
