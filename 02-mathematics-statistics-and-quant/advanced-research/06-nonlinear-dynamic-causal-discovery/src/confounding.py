"""Exactly aligned Gaussian lagged-predictability audit, not general causal discovery."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.stats import f, t

Array = NDArray[np.float64]


@dataclass(frozen=True)
class Sample:
    x_lag: Array
    y: Array
    z_lag2: Array
    z_wrong_lag: Array
    z_proxy: Array
    effect: float


def generate(n: int, effect: float, seed: int, proxy_noise_sd: float = 1.0) -> Sample:
    """Z_t iid; X_t=.8 Z_(t-1)+ux_t; Y_t=effect X_(t-1)+.8 Z_(t-2)+uy_t.

    Core (Xlag, Y, Zlag2) rows are independent despite the time labels.
    Wrong-lag ablation exposes adjacent Z values and has no exact F calibration claim.
    Innovations are Gaussian and mutually independent. No autoregressive term.
    """
    if (
        n < 5
        or not np.isfinite(effect)
        or not np.isfinite(proxy_noise_sd)
        or proxy_noise_sd < 0
    ):
        raise ValueError("n>=5, finite effect and nonnegative proxy noise required")
    rng = np.random.default_rng(seed)
    z = rng.normal(size=n + 2)
    ux = rng.normal(0, 0.5, size=n + 2)
    uy = rng.normal(0, 0.5, size=n + 2)
    x = np.zeros(n + 2)
    x[1:] = 0.8 * z[:-1] + ux[1:]
    idx = np.arange(2, n + 2)
    lag = x[idx - 1]
    conf = z[idx - 2]
    y = effect * lag + 0.8 * conf + uy[idx]
    return Sample(
        lag, y, conf, z[idx - 1], conf + rng.normal(0, proxy_noise_sd, n), effect
    )


@dataclass(frozen=True)
class TestResult:
    slope: float
    standard_error: float
    f_statistic: float
    p_value: float
    ci_low: float
    ci_high: float
    degrees_freedom: int


def lag_test(
    y: Array, x_lag: Array, controls: Array | None = None, alpha: float = 0.05
) -> TestResult:
    """Nested OLS F test for the final x column, with intercept and optional controls.

    Exact conditional F/t reference assumes full rank and iid Gaussian errors
    independent of the complete design. Time-series autocorrelation is unsupported.
    """
    y = np.asarray(y, dtype=float)
    x = np.asarray(x_lag, dtype=float)
    if y.ndim != 1 or x.ndim != 1 or len(x) != len(y) or not 0 < alpha < 1:
        raise ValueError("Matching vectors and alpha in (0,1) required")
    restricted = np.ones((len(y), 1))
    if controls is not None:
        c = np.asarray(controls, dtype=float)
        if c.ndim == 1:
            c = c[:, None]
        if c.ndim != 2 or len(c) != len(y):
            raise ValueError("Controls must have matching rows")
        restricted = np.column_stack([restricted, c])
    design = np.column_stack([restricted, x])
    if (
        len(y) <= design.shape[1]
        or not np.isfinite(design).all()
        or not np.isfinite(y).all()
    ):
        raise ValueError(
            "Finite observations and positive residual degrees of freedom required"
        )
    coef, _, rank, _ = np.linalg.lstsq(design, y, rcond=None)
    if rank != design.shape[1]:
        raise ValueError("Rank-deficient design")
    residual = y - design @ coef
    rss = float(residual @ residual)
    if rss <= np.finfo(float).tiny:
        raise ValueError("Zero residual variance")
    restricted_coef = np.linalg.lstsq(restricted, y, rcond=None)[0]
    restricted_residual = y - restricted @ restricted_coef
    rss0 = float(restricted_residual @ restricted_residual)
    df = len(y) - design.shape[1]
    statistic = max(0.0, (rss0 - rss) / (rss / df))
    inverse = np.linalg.pinv(design)
    variance = (rss / df) * float(inverse[-1] @ inverse[-1])
    se = float(np.sqrt(variance))
    slope = float(coef[-1])
    margin = float(t.ppf(1 - alpha / 2, df)) * se
    return TestResult(
        slope,
        se,
        statistic,
        float(f.sf(statistic, 1, df)),
        slope - margin,
        slope + margin,
        df,
    )


def paired_intervention(sample: Sample, shift: float) -> Array:
    """SCM intervention shift on X_(t-1), keeping all exogenous draws fixed."""
    if not np.isfinite(shift):
        raise ValueError("Finite intervention shift required")
    return sample.y + sample.effect * shift
