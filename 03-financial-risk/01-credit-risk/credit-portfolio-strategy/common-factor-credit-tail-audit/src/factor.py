"""Conditional finite credit distributions mixed over a standard normal factor."""

import math
from collections.abc import Sequence

from scipy.special import ndtr, ndtri, roots_hermitenorm

from src.base import independent_pmf, tail, validate


def common_factor_pmf(
    losses: Sequence[int], probabilities: Sequence[float], rho: float, nodes: int = 64
) -> list[float]:
    """rho is latent asset correlation, not default correlation; GH is numerical."""
    validate(losses, probabilities)
    if not math.isfinite(rho) or not 0 <= rho < 1:
        raise ValueError("latent correlation must be in [0,1)")
    if isinstance(nodes, bool) or not isinstance(nodes, int) or not 2 <= nodes <= 1024:
        raise ValueError("quadrature nodes must be integer2..1024")
    if rho == 0:
        return independent_pmf(losses, probabilities)
    x, w = roots_hermitenorm(nodes)
    thresholds = ndtri(probabilities)
    result = [0.0] * (sum(losses) + 1)
    for node, weight in zip(x, w):
        conditional = ndtr(
            (thresholds - math.sqrt(rho) * float(node)) / math.sqrt(1 - rho)
        )
        pmf = independent_pmf(losses, [float(value) for value in conditional])
        for index, mass in enumerate(pmf):
            result[index] += float(weight) * mass / math.sqrt(2 * math.pi)
    return result


def stability_passed(
    previous: Sequence[float],
    current: Sequence[float],
    confidence: float = 0.99,
    cdf_tolerance: float = 1e-5,
    es_tolerance: float = 0.01,
) -> bool:
    """Observed numerical stability only; not a certified bound on quadrature error."""
    if len(previous) != len(current):
        raise ValueError("matching lattice required")
    if any(not math.isfinite(t) or t < 0 for t in [cdf_tolerance, es_tolerance]):
        raise ValueError("finite nonnegative tolerances required")
    a = tail(previous, confidence)
    b = tail(current, confidence)
    delta = 0.0
    maximum = 0.0
    for p, q in zip(previous, current):
        delta += p - q
        maximum = max(maximum, abs(delta))
    return maximum <= cdf_tolerance and abs(a.es - b.es) <= es_tolerance
