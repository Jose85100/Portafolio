"""Finite independent Bernoulli portfolio oracle on an integer loss lattice."""

import math
from collections.abc import Sequence
from dataclasses import dataclass
from statistics import NormalDist


@dataclass(frozen=True)
class Tail:
    var: float
    es: float


def validate(losses: Sequence[int], probabilities: Sequence[float]) -> None:
    if len(losses) == 0 or len(losses) != len(probabilities):
        raise ValueError("matching nonempty inputs required")
    if any(isinstance(w, bool) or not isinstance(w, int) or w < 0 for w in losses):
        raise ValueError("losses must be nonnegative integer loss units")
    if sum(losses) > 20000:
        raise ValueError("loss lattice exceeds 20000 units; rescale explicitly")
    if any(not math.isfinite(p) or not 0 <= p <= 1 for p in probabilities):
        raise ValueError("probabilities must be finite and in [0,1]")


def independent_pmf(
    losses: Sequence[int], probabilities: Sequence[float]
) -> list[float]:
    """Multiply generating polynomials ((1-p)+p*z**loss); no discretization inside."""
    validate(losses, probabilities)
    pmf = [1.0]
    for weight, p in zip(losses, probabilities):
        updated = [0.0] * (len(pmf) + weight)
        for value, mass in enumerate(pmf):
            updated[value] += mass * (1 - p)
            updated[value + weight] += mass * p
        pmf = updated
    return pmf


def tail(pmf: Sequence[float], confidence: float = 0.99) -> Tail:
    if not math.isfinite(confidence) or not 0 < confidence < 1:
        raise ValueError("confidence strictly inside (0,1)")
    if len(pmf) == 0 or any(not math.isfinite(p) or p < 0 for p in pmf):
        raise ValueError("nonempty finite nonnegative pmf required")
    total = math.fsum(pmf)
    if not math.isclose(total, 1, rel_tol=0, abs_tol=1e-10):
        raise ValueError("pmf must conserve unit mass")
    cdf = 0.0
    var = float(len(pmf) - 1)
    for value, p in enumerate(pmf):
        cdf += p / total
        if cdf >= confidence:
            var = float(value)
            break
    remaining = 1 - confidence
    pieces = []
    for value in range(len(pmf) - 1, -1, -1):
        used = min(pmf[value] / total, remaining)
        pieces.append(value * used)
        remaining -= used
        if remaining <= 0:
            break
    return Tail(var, math.fsum(pieces) / (1 - confidence))


def normal_tail(
    losses: Sequence[int], probabilities: Sequence[float], confidence: float = 0.99
) -> Tail:
    validate(losses, probabilities)
    if not math.isfinite(confidence) or not 0 < confidence < 1:
        raise ValueError("confidence strictly inside (0,1)")
    mean = math.fsum(w * p for w, p in zip(losses, probabilities))
    variance = math.fsum(w * w * p * (1 - p) for w, p in zip(losses, probabilities))
    sigma = math.sqrt(variance)
    z = NormalDist().inv_cdf(confidence)
    return Tail(
        mean + sigma * z,
        mean + sigma * math.exp(-z * z / 2) / math.sqrt(2 * math.pi) / (1 - confidence),
    )
