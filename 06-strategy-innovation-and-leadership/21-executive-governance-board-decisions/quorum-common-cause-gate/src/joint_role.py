"""Sharp marginal-only AND bounds for the fixed synthetic committee event.

The mandatory role may depend arbitrarily on both reserves within each regime.
The normal regime needs only that role; the shock regime needs all three.
"""
from math import isfinite
from typing import TypedDict
from src.reserve_ambiguity import ReservePlan, bounds


class JointBounds(TypedDict):
    lower: float
    upper: float
    restricted_lower30: float
    nominal: float
    shock_lower: float
    shock_upper: float


def joint_bounds(plan: ReservePlan, shock: float = .2, risk: float = .95) -> JointBounds:
    """Return probabilities per session. Known marginal inputs are conditional.

    Bounds are sharp for this fixed event, not for arbitrary quorum rules.
    """
    old = bounds(plan, shock, risk)  # validates probability inputs
    lower = max(0.0, risk + plan.q1 + plan.q2 - 2)
    upper = min(risk, plan.q1, plan.q2)
    return {'lower': (1-shock)*risk + shock*lower,
            'upper': (1-shock)*risk + shock*upper,
            'restricted_lower30': old['lower_availability'],
            'nominal': old['nominal_availability'],
            'shock_lower': lower, 'shock_upper': upper}


def select_joint(plans: list[ReservePlan], target: float = .85,
                 shock: float = .2, risk: float = .95) -> ReservePlan:
    """Minimize menu cost subject to the full dependence lower bound."""
    if (not plans or len({p.name for p in plans}) != len(plans)
            or not isfinite(target) or not 0 <= target <= 1):
        raise ValueError('unique nonempty menu and finite target in [0,1] required')
    feasible = [p for p in plans if joint_bounds(p, shock, risk)['lower'] >= target-1e-12]
    if not feasible:
        raise ValueError('no authorized plan certifies target under joint ambiguity')
    return min(feasible, key=lambda p: (p.cost, p.name))
