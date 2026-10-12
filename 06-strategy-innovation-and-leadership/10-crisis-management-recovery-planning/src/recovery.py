"""Stress-response playbook with costed recovery actions."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class RecoveryAction:
    name: str
    one_time_cost: float
    monthly_savings: float
    implementation_month: int

def plan(initial_cash, monthly_inflows, monthly_outflows, horizon, actions, floor=0):
    if not isinstance(horizon,int) or horizon <= 0 or not all(isfinite(v) for v in
        (initial_cash,monthly_inflows,monthly_outflows,floor)):
        raise ValueError("invalid cash plan")
    if initial_cash < 0 or monthly_inflows < 0 or monthly_outflows < 0:
        raise ValueError("negative base inputs")
    if len({a.name for a in actions}) != len(actions):
        raise ValueError("duplicate actions")
    for a in actions:
        if not a.name or not all(isfinite(v) for v in (a.one_time_cost,a.monthly_savings)):
            raise ValueError("invalid action")
        if a.one_time_cost < 0 or a.monthly_savings < 0 or not isinstance(a.implementation_month,int) or a.implementation_month < 1:
            raise ValueError("invalid action economics")
    cash = initial_cash
    trajectory=[]
    first_breach = None
    for month in range(1,horizon+1):
        cost = sum(a.one_time_cost for a in actions if a.implementation_month==month)
        savings = sum(a.monthly_savings for a in actions if a.implementation_month<=month)
        cash += monthly_inflows-monthly_outflows+savings-cost
        trajectory.append({"month":month,"cash":cash})
        if first_breach is None and cash < floor:
            first_breach = month
    return {"trajectory":trajectory,"ending_cash":cash,
            "first_breach_month":first_breach,"recovery_achieved":first_breach is None}
