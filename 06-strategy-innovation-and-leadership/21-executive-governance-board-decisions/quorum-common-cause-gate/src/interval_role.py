"""Conditional certificates under assumed rectangular marginal uncertainty.

Input intervals are deterministic restrictions, never confidence intervals unless
an external simultaneous-coverage argument is supplied. No such data is used.
"""
from dataclasses import dataclass
from math import isfinite
from typing import TypedDict
from src.joint_role import joint_bounds
from src.reserve_ambiguity import ReservePlan


@dataclass(frozen=True)
class ProbabilityInterval:
    lower: float
    upper: float

    def __post_init__(self) -> None:
        if not (isfinite(self.lower) and isfinite(self.upper)
                and 0 <= self.lower <= self.upper <= 1):
            raise ValueError('probability interval must satisfy finite 0 <= lower <= upper <= 1')


@dataclass(frozen=True)
class IntervalPlan:
    name: str
    q1: ProbabilityInterval
    q2: ProbabilityInterval
    cost: float

    def __post_init__(self) -> None:
        if not self.name or not isfinite(self.cost) or self.cost < 0:
            raise ValueError('nonempty name and finite nonnegative cost required')


class IntervalBounds(TypedDict):
    lower: float
    upper: float


def interval_bounds(plan: IntervalPlan, risk: ProbabilityInterval,
                    shock: ProbabilityInterval) -> IntervalBounds:
    """Sharp envelope for the same fixed-quorum event as Oct31.

    Rectangular intervals permit simultaneous endpoint choices. The mandatory
    role has the same marginal in both regimes, as in the preceding component.
    """
    lo = joint_bounds(ReservePlan(plan.name, plan.q1.lower, plan.q2.lower, plan.cost),
                      shock.upper, risk.lower)['lower']
    hi = joint_bounds(ReservePlan(plan.name, plan.q1.upper, plan.q2.upper, plan.cost),
                      shock.lower, risk.upper)['upper']
    return {'lower': lo, 'upper': hi}


def select_interval(plans: list[IntervalPlan], risk: ProbabilityInterval,
                    shock: ProbabilityInterval, target: float = .85) -> IntervalPlan:
    if not plans or len({p.name for p in plans}) != len(plans) or not isfinite(target) or not 0 <= target <= 1:
        raise ValueError('unique nonempty menu and finite target in [0,1] required')
    feasible = [p for p in plans if interval_bounds(p, risk, shock)['lower'] >= target-1e-12]
    if not feasible:
        raise ValueError('no authorized plan certifies target for the assumed box')
    return min(feasible, key=lambda p: (p.cost, p.name))
