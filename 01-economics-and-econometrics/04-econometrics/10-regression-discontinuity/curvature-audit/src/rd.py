"""Sharp-RD point estimate: uniform kernel, separate local linear slopes.

Estimates a discontinuity, not causal identification by itself. Causal reading
requires continuity of potential-outcome expectations at the threshold.
"""

from __future__ import annotations
import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]


def intercept(x: Array, y: Array) -> float:
    """Centered OLS intercept; reject numerically singular within-side support."""
    xc = x - x.mean()
    scale = float(xc @ xc)
    if scale <= np.finfo(float).eps * max(1.0, float(x @ x)):
        raise ValueError("Numerically singular within-side support")
    slope = float(xc @ (y - y.mean())) / scale
    return float(y.mean() - slope * x.mean())


def estimate(
    x: Array, y: Array, bandwidth: float, cutoff: float = 0.0, min_side: int = 8
) -> tuple[float, int, int]:
    """Right-minus-left intercepts within |x-cutoff|<=h; h=1 global in DGP."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.ndim != 1 or y.ndim != 1 or x.size != y.size:
        raise ValueError("Equal-sized one-dimensional vectors required")
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("Finite observations required")
    if not np.isfinite(bandwidth) or bandwidth <= 0 or not np.isfinite(cutoff):
        raise ValueError("Finite cutoff and positive finite bandwidth required")
    if min_side < 2:
        raise ValueError("At least two points per side required")
    running = x - cutoff
    left = (running < 0) & (running >= -bandwidth)
    right = (running >= 0) & (running <= bandwidth)
    nl, nr = int(left.sum()), int(right.sum())
    if min(nl, nr) < min_side:
        raise ValueError("Insufficient observations per side")
    return (
        intercept(running[right], y[right]) - intercept(running[left], y[left]),
        nl,
        nr,
    )


def sample(
    seed: int,
    n: int,
    curvature: float = 4.0,
    latent_jump: float = 0.0,
    noise_sd: float = 0.3,
) -> tuple[Array, Array]:
    """True treatment effect=1; curvature continuous, latent_jump violates continuity.

    Y0=.4x+3x²+curvature*I(x>=0)x²+latent_jump*I(x>=0)+noise.
    """
    if (
        n < 4
        or not np.isfinite([curvature, latent_jump, noise_sd]).all()
        or noise_sd < 0
    ):
        raise ValueError("n>=4, finite parameters and nonnegative noise required")
    rng = np.random.default_rng(seed)
    x = rng.uniform(-1, 1, n)
    t = x >= 0
    y = (
        0.4 * x
        + 3 * x * x
        + curvature * t * x * x
        + latent_jump * t
        + t
        + noise_sd * rng.normal(size=n)
    )
    return x, y
