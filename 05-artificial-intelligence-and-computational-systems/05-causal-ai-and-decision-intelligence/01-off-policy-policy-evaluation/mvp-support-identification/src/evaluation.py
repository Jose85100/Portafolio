"""Finite-context OPE: structural support and sampling uncertainty separated.

Known population context probabilities and known randomized logging policy.
Rewards are IID conditional on (context, action), fixed target independent of log.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import isclose, isfinite, log, sqrt

Observation = tuple[int, int, float]


@dataclass(frozen=True)
class Design:
    context: tuple[float, ...]
    logging: tuple[tuple[float, ...], ...]
    target: tuple[tuple[float, ...], ...]

    def validate(self) -> None:
        c = len(self.context)
        if not c or len(self.logging) != c or len(self.target) != c:
            raise ValueError("context/policy dimensions mismatch")
        a = len(self.logging[0])
        if not a or any(len(row) != a for row in (*self.logging, *self.target)):
            raise ValueError("action dimensions mismatch")
        for row in (self.context, *self.logging, *self.target):
            if any(not isfinite(x) or x < 0 or x > 1 for x in row) or not isclose(
                sum(row), 1.0, abs_tol=1e-12, rel_tol=0
            ):
                raise ValueError(
                    "probability vectors must be finite, nonnegative and sum to one"
                )


@dataclass(frozen=True)
class Audit:
    lower: float
    upper: float
    unsupported_mass: float
    unseen_supported_mass: float
    observed_contribution: float
    midpoint: float
    ips_truncated: float
    snips_supported: float | None
    counts: tuple[tuple[int, ...], ...]
    sums: tuple[tuple[float, ...], ...]


def evaluate(
    design: Design, observations: Sequence[Observation], delta: float = 0.05
) -> Audit:
    """Simultaneous cell-Hoeffding envelope; unknown cells contribute [0,weight].

    With conditional IID bounded rewards, union bound over C*A cells gives
    coverage >=1-delta for value under the *known* design. This is fixed-n,
    not an anytime, adaptive-logging, estimated-propensity guarantee.
    """
    design.validate()
    if not isfinite(delta) or not 0 < delta < 1:
        raise ValueError("delta must be between zero and one")
    c, a = len(design.context), len(design.logging[0])
    counts = [[0] * a for _ in range(c)]
    sums = [[0.0] * a for _ in range(c)]
    ips = weight_sum = 0.0
    for x, action, reward in observations:
        if (
            type(x) is not int
            or type(action) is not int
            or not 0 <= x < c
            or not 0 <= action < a
        ):
            raise ValueError("invalid context/action index")
        if not isfinite(reward) or not 0 <= reward <= 1:
            raise ValueError("reward must lie in [0,1]")
        if design.context[x] == 0 or design.logging[x][action] == 0:
            raise ValueError("log contains an event impossible under declared design")
        counts[x][action] += 1
        sums[x][action] += reward
        weight = design.target[x][action] / design.logging[x][action]
        ips += weight * reward
        weight_sum += weight
    lower = upper = unsupported = unseen = contribution = 0.0
    for x in range(c):
        for action in range(a):
            weight = design.context[x] * design.target[x][action]
            if design.logging[x][action] == 0:
                unsupported += weight
                upper += weight
            elif counts[x][action] == 0:
                unseen += weight
                upper += weight
            else:
                mean = sums[x][action] / counts[x][action]
                radius = sqrt(log(2 * c * a / delta) / (2 * counts[x][action]))
                contribution += weight * mean
                lower += weight * max(0.0, mean - radius)
                upper += weight * min(1.0, mean + radius)
    midpoint = contribution + 0.5 * (unsupported + unseen)
    return Audit(
        lower,
        upper,
        unsupported,
        unseen,
        contribution,
        midpoint,
        ips / len(observations) if observations else 0.0,
        ips / weight_sum if weight_sum else None,
        tuple(tuple(row) for row in counts),
        tuple(tuple(row) for row in sums),
    )


def interval_decision(lower: float, upper: float, threshold: float = 0.5) -> str:
    if (
        not all(isfinite(x) for x in (lower, upper, threshold))
        or not 0 <= lower <= upper <= 1
        or not 0 <= threshold <= 1
    ):
        raise ValueError("invalid reward interval or threshold")
    return (
        "accept" if lower > threshold else "reject" if upper < threshold else "abstain"
    )
