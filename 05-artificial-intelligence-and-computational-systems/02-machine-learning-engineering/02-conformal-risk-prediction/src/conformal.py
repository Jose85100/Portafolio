"""Finite-sample weighted split conformal with explicit test-point mass.

Scores must come from a predictor fixed independently of calibration data.
The guarantee requires known density ratios and invariant Y|X.
"""

from __future__ import annotations
import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]


def thresholds(
    scores: Array,
    weights: Array,
    test_weights: Array,
    alpha: float = 0.1,
    include_test_mass: bool = True,
) -> Array:
    """Return weighted quantiles; insufficient finite mass returns infinity.

    Sort once O(n log n), then binary search for m test weights O(m log n).
    No clipping or silent renormalization of test mass is permitted.
    """
    s, w, t = (np.asarray(a, dtype=float) for a in (scores, weights, test_weights))
    if s.ndim != 1 or w.shape != s.shape or t.ndim != 1 or len(s) == 0 or len(t) == 0:
        raise ValueError("nonempty 1D scores and matching weights required")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between zero and one")
    if any(not np.all(np.isfinite(a)) for a in (s, w, t)):
        raise ValueError("inputs must be finite")
    if np.any(s < 0) or np.any(w <= 0) or np.any(t <= 0):
        raise ValueError("scores nonnegative; density ratios strictly positive")
    # A common rescaling prevents overflow without changing probabilities.
    scale = max(float(w.max()), float(t.max()))
    w, t = w / scale, t / scale
    if np.any(w == 0) or np.any(t == 0):
        raise ValueError("density ratio dynamic range exceeds floating-point support")
    order = np.argsort(s, kind="stable")
    cumulative = np.cumsum(w[order])
    target = (1 - alpha) * (
        cumulative[-1] + (t if include_test_mass else np.zeros_like(t))
    )
    index = np.searchsorted(cumulative, target, side="left")
    result = np.full(len(t), np.inf)
    finite = index < len(s)
    result[finite] = s[order][index[finite]]
    return result


def ratios(group: NDArray[np.bool_], source: float, target: float) -> Array:
    """Known Bernoulli covariate likelihood ratios, never estimated from labels."""
    if not (0 < source < 1 and 0 < target < 1):
        raise ValueError("overlap requires probabilities strictly inside (0,1)")
    return np.where(group, target / source, (1 - target) / (1 - source))
