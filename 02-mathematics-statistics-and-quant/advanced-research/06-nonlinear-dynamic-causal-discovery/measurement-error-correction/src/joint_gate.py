"""28October: a necessary full latent-covariance check, not causal certification."""

import numpy as np
from numpy.typing import NDArray

from src.moments import Estimate, correct_covariance


def correct_covariance_joint(
    covariance: NDArray[np.float64],
    noise_variance: float,
    max_condition: float = 100.0,
    tolerance: float = 1e-10,
) -> Estimate:
    """Require Cov(X,Z,Y)=Cov(X,W,Y)-diag(0,Var(v),0) to be PSD.

    Classical independent measurement error is an assumption. Passing this
    necessary moment check cannot establish that the assumed variance is true.
    Correlation normalization keeps the check invariant to positive unit changes.
    Floating tolerance is explicit; this is not directed-rounding certification.
    """
    if not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("Finite nonnegative tolerance required")
    baseline = correct_covariance(covariance, noise_variance, max_condition)
    if baseline.status != "accepted":
        return baseline
    latent = np.asarray(covariance, dtype=float).copy()
    latent[1, 1] -= noise_variance
    diagonal = np.diag(latent)
    if np.any(diagonal < 0):
        return Estimate(None, "incompatible_joint_covariance", baseline.condition)
    scale = np.sqrt(np.where(diagonal > 0, diagonal, 1.0))
    correlation = latent / np.outer(scale, scale)
    if np.linalg.eigvalsh(correlation)[0] < -tolerance:
        return Estimate(None, "incompatible_joint_covariance", baseline.condition)
    return baseline
