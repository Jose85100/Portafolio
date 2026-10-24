"""Conditional area-sign certificate for a sampled Lipschitz planar curve.

The speed bound is a user-supplied assumption, never estimated from the samples.
"""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from src.signatures import polygon_area

Array = NDArray[np.float64]


@dataclass(frozen=True)
class Certificate:
    """Area/sign diagnostics; certify_area supplies a conditional radius bound."""

    area: float
    radius: float
    sign: int
    segments: int


def certify_area(path: Array, times: Array, speed_bound: float) -> Certificate:
    """Bound arc/chord error by sum((L*dt)^2)/2 on [times[0], times[-1]].

    The curve must be planar and L-Lipschitz in Euclidean norm with respect to
    supplied times. Open curves are closed by the straight endpoint chord.
    Sample secant consistency is necessary, but NOT sufficient, for this bound.
    """
    x = np.asarray(path, dtype=float)
    t = np.asarray(times, dtype=float)
    if (
        x.ndim != 2
        or x.shape[1] != 2
        or len(x) < 2
        or t.ndim != 1
        or len(t) != len(x)
        or not np.isfinite(x).all()
        or not np.isfinite(t).all()
        or not np.isfinite(speed_bound)
        or speed_bound < 0
    ):
        raise ValueError(
            "Finite planar samples, matching times and nonnegative L required"
        )
    dt = np.diff(t)
    if np.any(dt <= 0):
        raise ValueError("Times must be strictly increasing")
    if np.any(np.linalg.norm(np.diff(x, axis=0), axis=1) > speed_bound * dt + 1e-12):
        raise ValueError("Samples contradict supplied speed bound")
    area = polygon_area(x)
    radius = float(0.5 * speed_bound**2 * np.dot(dt, dt))
    sign = 1 if area > radius else (-1 if area < -radius else 0)
    return Certificate(area, radius, sign, len(x) - 1)


def refine_sign(
    curve: Callable[[Array], Array],
    speed_bound: float,
    initial_segments: int = 4,
    max_segments: int = 4096,
) -> Certificate:
    """Double sampling until the conditional interval excludes zero or budget ends."""
    if initial_segments < 2 or max_segments < initial_segments:
        raise ValueError("Invalid refinement budget")
    n = initial_segments
    while True:
        times = np.linspace(0.0, 1.0, n + 1)
        result = certify_area(curve(times), times, speed_bound)
        if result.sign != 0 or n == max_segments:
            return result
        n = min(2 * n, max_segments)


def plateau_stop(
    curve: Callable[[Array], Array],
    tolerance: float = 1e-10,
    initial_segments: int = 4,
    max_segments: int = 4096,
) -> Certificate:
    """Comparator: stop when two successive polygon areas agree; no certificate."""
    if tolerance < 0 or initial_segments < 2 or max_segments < initial_segments:
        raise ValueError("Invalid plateau parameters")
    n = initial_segments
    previous = polygon_area(curve(np.linspace(0.0, 1.0, n + 1)))
    while n < max_segments:
        n = min(2 * n, max_segments)
        area = polygon_area(curve(np.linspace(0.0, 1.0, n + 1)))
        change = abs(area - previous)
        if change <= tolerance:
            return Certificate(
                area, change, int(np.sign(area)) if abs(area) > tolerance else 0, n
            )
        previous = area
    return Certificate(previous, float("nan"), int(np.sign(previous)), n)
