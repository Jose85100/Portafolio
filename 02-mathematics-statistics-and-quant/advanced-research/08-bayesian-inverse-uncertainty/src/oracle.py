"""80-digit oracle for the actual float64 inputs, not idealized singular factors."""

import mpmath as mp
import numpy as np
from src.posterior import Array, Posterior


class Oracle:
    def __init__(self, a: Array, sigma: float, tau: float = 1.0) -> None:
        with mp.workdps(80):
            matrix = mp.matrix(a.tolist())
            noise, prior = mp.mpf(float(sigma)), mp.mpf(float(tau))
            precision = matrix.T * matrix / noise**2 + mp.eye(a.shape[1]) / prior**2
            self.cov = precision**-1
            self.gain = self.cov * matrix.T / noise**2

    def evaluate(self, y: Array) -> Posterior:
        with mp.workdps(80):
            mean = self.gain * mp.matrix(y.tolist())
            return Posterior(
                np.array([float(v) for v in mean]), np.array(self.cov.tolist(), dtype=float)
            )
