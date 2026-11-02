"""Conditional lower certificates with a supplied pair co-attendance floor.

The floor is a hypothetical constraint, not an estimated confidence bound.
No automatic decision can authorize treating it as observed evidence.
"""
from math import isfinite
from src.interval_role import IntervalPlan, ProbabilityInterval, interval_bounds


def pair_lower(plan: IntervalPlan, risk: ProbabilityInterval,
               shock: ProbabilityInterval, pair_floor: float = 0.0) -> float:
    """Sharp lower probability for this fixed event and nonempty constraint set."""
    if not isfinite(pair_floor) or not 0 <= pair_floor <= min(plan.q1.upper, plan.q2.upper):
        raise ValueError('pair floor must be finite, nonnegative and feasible for both upper marginals')
    joint_min = max(pair_floor, plan.q1.lower+plan.q2.lower-1, 0.0)
    return (1-shock.upper)*risk.lower + shock.upper*max(0.0, risk.lower+joint_min-1)


def required_pair_floor(plan: IntervalPlan, risk: ProbabilityInterval,
                        shock: ProbabilityInterval, target: float = .85) -> float:
    """Smallest supplied floor sufficient for target; raises if unattainable.

    Returns zero when the box alone already certifies target. The returned
    threshold describes a requirement, never proof that the requirement holds.
    """
    if not isfinite(target) or not 0 <= target <= 1:
        raise ValueError('finite target in [0,1] required')
    if interval_bounds(plan, risk, shock)['lower'] >= target-1e-12:
        return 0.0
    if shock.upper == 0:
        raise ValueError('pair evidence cannot repair an insufficient mandatory-role bound')
    need = (target-(1-shock.upper)*risk.lower)/shock.upper + 1-risk.lower
    cap = min(plan.q1.upper, plan.q2.upper)
    if need > cap+1e-12:
        raise ValueError('no feasible pair floor certifies target')
    return min(cap, max(0.0, need))


def choose_pair(plans: list[IntervalPlan], risk: ProbabilityInterval,
                shock: ProbabilityInterval, floors: dict[str, float],
                target: float = .85) -> IntervalPlan:
    if (not plans or len({p.name for p in plans}) != len(plans)
            or set(floors) != {p.name for p in plans}
            or not isfinite(target) or not 0 <= target <= 1):
        raise ValueError('unique nonempty menu, exact floor keys and target in [0,1] required')
    feasible = [p for p in plans if pair_lower(p, risk, shock, floors[p.name]) >= target-1e-12]
    if not feasible:
        raise ValueError('no authorized option certifies target with supplied constraints')
    return min(feasible, key=lambda p: (p.cost, p.name))
