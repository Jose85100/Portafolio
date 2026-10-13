"""Unbiased ordinary importance sampling for a disconnected Gaussian event."""

from dataclasses import dataclass
import math
import numpy as np
from numpy.typing import NDArray
from scipy.integrate import quad
from scipy.special import logsumexp, ndtr

Array = NDArray[np.float64]
METHODS = ("direct", "single_tilt", "balanced", "defensive")


@dataclass(frozen=True)
class Estimate:
    mean: float
    se: float
    left_hits: int
    right_hits: int
    contribution_ess: float


def validate_threshold(a: float) -> None:
    if not math.isfinite(a) or not 0 < a <= 8:
        raise ValueError("threshold must be finite and in (0, 8]")


def truth(a: float) -> float:
    validate_threshold(a)
    return float(2 * ndtr(-a))


def proposal(a: float, method: str) -> tuple[Array, Array]:
    validate_threshold(a)
    if method == "direct":
        return np.array([0.0]), np.array([1.0])
    if method == "single_tilt":
        return np.array([a]), np.array([1.0])
    if method == "balanced":
        return np.array([-a, a]), np.array([0.5, 0.5])
    if method == "defensive":
        return np.array([0.0, -a, a]), np.array([0.1, 0.45, 0.45])
    raise ValueError(f"unknown method: {method}")


def log_weight(x: Array, a: float, method: str) -> Array:
    means, probabilities = proposal(a, method)
    # Common normalizing constants cancel. Use full mixture density, never
    # the density of only the randomly selected component.
    log_q = logsumexp(np.log(probabilities) - 0.5 * (x[:, None] - means) ** 2, axis=1)
    return np.asarray(-0.5 * x * x - log_q, dtype=np.float64)


def estimate(a: float, n: int, seed: int, method: str) -> Estimate:
    if isinstance(n, bool) or not isinstance(n, int) or n < 2:
        raise ValueError("n must be an integer >= 2")
    means, probabilities = proposal(a, method)
    rng = np.random.default_rng(seed)
    components = rng.choice(len(means), size=n, p=probabilities)
    x = rng.normal(size=n) + means[components]
    y = np.zeros(n, dtype=np.float64)
    event = np.abs(x) > a
    y[event] = np.exp(log_weight(x[event], a, method))
    total, squares = float(y.sum()), float(y @ y)
    return Estimate(
        float(y.mean()),
        float(y.std(ddof=1) / np.sqrt(n)),
        int((x < -a).sum()),
        int((x > a).sum()),
        total * total / squares if squares else 0.0,
    )


def population_variance(a: float, method: str) -> float:
    """Per-draw variance; closed form for direct/single, quadrature for mixtures."""
    probability = truth(a)
    proposal(a, method)
    if method == "direct":
        return probability * (1 - probability)
    if method == "single_tilt":
        # phi(x)^2/phi(x-a) = exp(a^2) phi(x+a).
        second = math.exp(a * a) * (ndtr(0.0) + ndtr(-2 * a))
    else:

        def integrand(x: float) -> float:
            log_p = -0.5 * x * x - 0.5 * math.log(2 * math.pi)
            lw = float(log_weight(np.array([x]), a, method)[0])
            return math.exp(log_p + lw)

        second = sum(
            quad(integrand, lo, hi, epsabs=1e-40, epsrel=1e-9)[0]
            for lo, hi in [(-np.inf, -a), (a, np.inf)]
        )
    return float(second - probability * probability)
