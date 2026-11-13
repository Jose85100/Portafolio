"""Scalar OU transitions and explicit finite-sample diagnostic failures.

dX = -kappa X dt + sigma dW. Mean is known to be zero throughout.
The supported domain is deliberately bounded for float64 reproducibility.
"""

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.signal import lfilter

Array = NDArray[np.float64]


@dataclass(frozen=True)
class Transition:
    phi: float
    innovation_variance: float


def validate(kappa: float, sigma: float, dt: float) -> None:
    """Reject unsupported inputs instead of silently clipping them."""
    if not all(math.isfinite(v) for v in (kappa, sigma, dt)):
        raise ValueError("parameters must be finite")
    if not (0 < kappa <= 100 and 0 <= sigma <= 100 and 0 < dt <= 100):
        raise ValueError("require 0<kappa,dt<=100 and 0<=sigma<=100")
    if not 1e-12 <= kappa * dt <= 100:
        raise ValueError("require 1e-12<=kappa*dt<=100")


def exact_transition(kappa: float, sigma: float, dt: float) -> Transition:
    """Exact Gaussian transition using expm1 near the Brownian limit."""
    validate(kappa, sigma, dt)
    phi = math.exp(-kappa * dt)
    q = sigma**2 * (-math.expm1(-2 * kappa * dt)) / (2 * kappa)
    return Transition(phi, q)


def euler_transition(kappa: float, sigma: float, dt: float) -> Transition:
    """Euler baseline; deliberately permits unstable steps for auditing."""
    validate(kappa, sigma, dt)
    return Transition(1 - kappa * dt, sigma**2 * dt)


def stationary_variance(transition: Transition) -> float:
    """Stationary variance exists only when |phi|<1."""
    if not math.isfinite(transition.phi) or abs(transition.phi) >= 1:
        raise ValueError("no stable stationary AR(1) distribution")
    if not math.isfinite(transition.innovation_variance) or transition.innovation_variance < 0:
        raise ValueError("invalid innovation variance")
    return transition.innovation_variance / ((1 - transition.phi) * (1 + transition.phi))


def finite_variance(transition: Transition, steps: int) -> float:
    """Variance after steps starting at X0=0, including unstable baselines."""
    if not isinstance(steps, int) or isinstance(steps, bool) or not 0 <= steps <= 10000:
        raise ValueError("steps must be an integer in [0,10000]")
    if not (math.isfinite(transition.phi) and math.isfinite(transition.innovation_variance)):
        raise ValueError("non-finite transition")
    if transition.innovation_variance < 0:
        raise ValueError("negative innovation variance")
    variance = 0.0
    for _ in range(steps):
        variance = transition.phi**2 * variance + transition.innovation_variance
        if not math.isfinite(variance):
            raise ValueError("finite variance overflow")
    return variance


def simulate(transition: Transition, innovations: Array, *, stationary: bool = False) -> Array:
    """Rows are paths. Column zero is X0; other columns are time steps.

    Gaussian innovations are passed explicitly so RNG seeds and pairing remain
    external. By default X0=0; stationary=True uses an independent stationary X0.
    """
    z = np.asarray(innovations, dtype=np.float64)
    if z.ndim != 2 or min(z.shape) < 1 or not np.isfinite(z).all():
        raise ValueError("innovations must be a nonempty finite 2D array")
    finite_variance(transition, 0)
    inputs = z * math.sqrt(transition.innovation_variance)
    inputs[:, 0] = z[:, 0] * math.sqrt(stationary_variance(transition)) if stationary else 0
    with np.errstate(over="raise", invalid="raise"):
        result = np.asarray(lfilter([1.0], [1.0, -transition.phi], inputs, axis=1))
    if not np.isfinite(result).all():
        raise ValueError("simulation overflow")
    return result


def diagnostics(paths: Array, dt: float) -> tuple[Array, Array, Array]:
    """Known-zero-mean second moment, conditional OLS phi and -log(phi)/dt.

    Undefined OU rates (phi<=0 or phi>=1) remain NaN; never clip estimates.
    This is not sample-demeaned Pearson autocorrelation or a unit-root test.
    """
    x = np.asarray(paths, dtype=np.float64)
    if x.ndim != 2 or x.shape[0] < 1 or x.shape[1] < 3 or not np.isfinite(x).all():
        raise ValueError("need finite paths of length >=3")
    if not math.isfinite(dt) or dt <= 0:
        raise ValueError("dt must be finite and positive")
    second_moment = np.mean(x * x, axis=1)
    denominator = np.sum(x[:, :-1] ** 2, axis=1)
    phi = np.full(x.shape[0], np.nan)
    np.divide(np.sum(x[:, :-1] * x[:, 1:], axis=1), denominator, out=phi, where=denominator > 0)
    kappa = np.full_like(phi, np.nan)
    valid = (phi > 0) & (phi < 1)
    kappa[valid] = -np.log(phi[valid]) / dt
    return second_moment, phi, kappa
