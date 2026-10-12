"""Exact budget-constrained initiative selection with dependencies."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Initiative:
    name: str
    cost: int
    scenario_benefits: tuple
    dependencies: tuple = ()

def optimize(initiatives, budget, scenario_probabilities):
    if budget < 0 or not isinstance(budget, int):
        raise ValueError("budget must be nonnegative integer")
    if not initiatives or len(initiatives) > 22:
        raise ValueError("supports 1 to 22 initiatives (exponential exact search)")
    if len({x.name for x in initiatives}) != len(initiatives):
        raise ValueError("duplicate initiative names")
    if not scenario_probabilities or any(not isfinite(p) or p < 0 for p in scenario_probabilities):
        raise ValueError("invalid scenario probabilities")
    if abs(sum(scenario_probabilities)-1) > 1e-10:
        raise ValueError("probabilities must sum to one")
    names = {x.name for x in initiatives}
    for x in initiatives:
        if not x.name or not isinstance(x.cost,int) or x.cost < 0:
            raise ValueError("invalid cost or name")
        if len(x.scenario_benefits) != len(scenario_probabilities):
            raise ValueError("scenario dimensions differ")
        if any(not isfinite(b) for b in x.scenario_benefits):
            raise ValueError("non-finite benefits")
        if any(dep not in names or dep == x.name for dep in x.dependencies):
            raise ValueError("invalid dependency")
    best_value = 0.0
    best_names = ()
    best_cost = 0
    # Exhaustive search is intentional: exact optimum for small portfolios.
    for mask in range(1 << len(initiatives)):
        selected = {x.name for i,x in enumerate(initiatives) if mask & (1 << i)}
        if any(not set(x.dependencies).issubset(selected) for x in initiatives if x.name in selected):
            continue
        cost = sum(x.cost for x in initiatives if x.name in selected)
        if cost > budget:
            continue
        benefit = sum(sum(p*b for p,b in zip(scenario_probabilities,x.scenario_benefits))
                      for x in initiatives if x.name in selected)
        net = benefit-cost
        if net > best_value + 1e-12 or (abs(net-best_value) <= 1e-12 and cost < best_cost):
            best_value, best_names, best_cost = net, tuple(sorted(selected)), cost
    return {"selected": best_names, "total_cost": best_cost,
            "expected_net_benefit": best_value, "unused_budget": budget-best_cost}
