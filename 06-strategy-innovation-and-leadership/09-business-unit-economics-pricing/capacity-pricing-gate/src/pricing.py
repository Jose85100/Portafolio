"""Finite-menu pricing under capacity and exact discrete CVaR shortfall budget."""
from dataclasses import dataclass
from math import exp, isfinite
from typing import TypedDict


class Decision(TypedDict):
    price: float | None
    expected_profit: float
    cvar_shortfall: float
    scenario_profits: list[float]


@dataclass(frozen=True)
class Scenario:
    name: str
    weight: float
    arrivals: float
    intercept: float = 5.0
    elasticity: float = 0.25

    def __post_init__(self) -> None:
        if not all(isfinite(x) for x in (self.weight, self.arrivals, self.intercept, self.elasticity)):
            raise ValueError('finite scenario parameters required')
        if self.weight <= 0 or self.arrivals < 0 or self.elasticity <= 0:
            raise ValueError('positive weight/elasticity and nonnegative arrivals required')


def profit(price: float, scenario: Scenario, capacity: float,
           unit_cost: float, fixed_cost: float) -> float:
    """Fluid expected-demand approximation, not realized integer transactions."""
    if not all(isfinite(x) and x >= 0 for x in (price, capacity, unit_cost, fixed_cost)):
        raise ValueError('finite nonnegative price/capacity/costs required')
    logit = scenario.intercept - scenario.elasticity * price
    probability = 1 / (1 + exp(-logit)) if logit >= 0 else exp(logit) / (1 + exp(logit))
    served = min(capacity, scenario.arrivals * probability)
    return (price - unit_cost) * served - fixed_cost


def cvar(losses: list[float], weights: list[float], alpha: float) -> float:
    """Average worst (1-alpha) mass, splitting boundary atoms exactly."""
    if (not losses or len(losses) != len(weights)
            or not isfinite(alpha) or not 0 <= alpha < 1
            or not all(isfinite(x) for x in losses)
            or not all(isfinite(w) and w > 0 for w in weights)
            or abs(sum(weights) - 1) > 1e-10):
        raise ValueError('normalized positive weights, finite losses and 0<=alpha<1 required')
    remaining, tail = 1 - alpha, 0.0
    for loss, weight in sorted(zip(losses, weights), reverse=True):
        mass = min(remaining, weight)
        tail += mass * loss
        remaining -= mass
        if remaining <= 1e-15:
            break
    return tail / (1 - alpha)


def evaluate(price: float | None, scenarios: list[Scenario], capacity: float,
             unit_cost: float, fixed_cost: float, alpha: float) -> Decision:
    values = ([profit(price, s, capacity, unit_cost, fixed_cost) for s in scenarios]
              if price is not None else [0.0 for _ in scenarios])
    weights = [s.weight for s in scenarios]
    downside = cvar([max(-v, 0.0) for v in values], weights, alpha)
    return {'price': price, 'expected_profit': sum(w*v for w, v in zip(weights, values)),
            'cvar_shortfall': downside, 'scenario_profits': values}


def choose(prices: list[float], scenarios: list[Scenario], capacity: float,
           unit_cost: float, fixed_cost: float, alpha: float,
           budget: float | None = None) -> Decision:
    if not prices or (budget is not None and (not isfinite(budget) or budget < 0)):
        raise ValueError('nonempty price menu and nonnegative finite budget required')
    rows = [evaluate(p, scenarios, capacity, unit_cost, fixed_cost, alpha)
            for p in [None, *sorted(set(prices))]]
    feasible = [r for r in rows if budget is None or float(r['cvar_shortfall']) <= budget + 1e-10]
    return max(feasible, key=lambda r: float(r['expected_profit']))
