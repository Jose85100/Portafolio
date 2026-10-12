"""Board-level capital allocation under a finite investment budget."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class BusinessUnit:
    name: str
    capital_required: int
    expected_nopat: float
    wacc: float
    max_allocation: int = 1

def allocate(units, budget):
    if not isinstance(budget, int) or budget < 0 or not 0 < len(units) <= 22:
        raise ValueError("invalid budget or portfolio size")
    if len({u.name for u in units}) != len(units):
        raise ValueError("duplicate unit")
    for u in units:
        if not u.name or not isinstance(u.capital_required,int) or u.capital_required <= 0:
            raise ValueError("invalid capital requirement")
        if not isfinite(u.expected_nopat) or not isfinite(u.wacc) or not 0 <= u.wacc <= 1:
            raise ValueError("invalid economic inputs")
        if u.max_allocation != 1:
            raise ValueError("this model only supports binary investment")
    best_value, best_cost, best = 0.0, 0, ()
    for mask in range(1 << len(units)):
        selected = [u for i,u in enumerate(units) if mask & (1 << i)]
        cost = sum(u.capital_required for u in selected)
        if cost > budget:
            continue
        eva = sum(u.expected_nopat-u.wacc*u.capital_required for u in selected)
        if eva > best_value + 1e-10 or (abs(eva-best_value) <= 1e-10 and cost < best_cost):
            best_value, best_cost = eva, cost
            best = tuple(sorted(u.name for u in selected))
    return {"selected":best,"capital_used":best_cost,"expected_eva":best_value,
            "capital_remaining":budget-best_cost,
            "unit_roic":{u.name:u.expected_nopat/u.capital_required for u in units}}
