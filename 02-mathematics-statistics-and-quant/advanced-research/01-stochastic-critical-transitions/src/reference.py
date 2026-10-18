"""Independent covariance integral via Van Loan's block exponential."""

import math

import numpy as np
from scipy.linalg import expm

from src.ou import Transition


def matrix_transition(kappa: float, sigma: float, dt: float) -> Transition:
    """For moderate |kappa dt|, exp([[A,BB'],[0,-A']]*dt)."""
    if not all(math.isfinite(v) for v in (kappa, sigma, dt)):
        raise ValueError("non-finite parameters")
    if kappa <= 0 or sigma < 0 or dt <= 0 or not 1e-12 <= kappa * dt <= 20:
        raise ValueError("oracle supports 1e-12<=kappa*dt<=20")
    block = np.array([[-kappa, sigma**2], [0, kappa]]) * dt
    result = expm(block)
    return Transition(float(result[0, 0]), float(result[0, 1] * result[0, 0]))
