"""Cash runway and liquidity covenant stress engine."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Scenario:
    name: str
    probability: float
    revenue_multiplier: float
    cost_multiplier: float
    collection_delay_months: int = 0

def evaluate(initial_cash, monthly_revenue, monthly_cost, horizon, scenarios,
             minimum_cash=0.0):
    values = (initial_cash,monthly_revenue,monthly_cost,minimum_cash)
    if not all(isfinite(v) for v in values) or any(v < 0 for v in values[:3]):
        raise ValueError("invalid cash flows")
    if not isinstance(horizon,int) or horizon < 1:
        raise ValueError("horizon must be positive")
    if not scenarios or abs(sum(s.probability for s in scenarios)-1) > 1e-10:
        raise ValueError("scenario probabilities must sum to one")
    rows = []
    for s in scenarios:
        if not s.name or not all(isfinite(v) for v in
                (s.probability,s.revenue_multiplier,s.cost_multiplier)):
            raise ValueError("invalid scenario")
        if s.probability < 0 or s.revenue_multiplier < 0 or s.cost_multiplier < 0:
            raise ValueError("negative scenario parameter")
        if not isinstance(s.collection_delay_months,int) or s.collection_delay_months < 0:
            raise ValueError("invalid collection delay")
        cash = initial_cash
        first_breach = None
        minimum = cash
        for month in range(1,horizon+1):
            inflow = monthly_revenue*s.revenue_multiplier if month > s.collection_delay_months else 0
            cash += inflow-monthly_cost*s.cost_multiplier
            minimum = min(minimum,cash)
            if first_breach is None and cash < minimum_cash:
                first_breach = month
        rows.append({"scenario":s.name,"probability":s.probability,
                     "ending_cash":cash,"minimum_cash":minimum,
                     "first_breach_month":first_breach})
    return {"scenarios":rows,
            "breach_probability":sum(r["probability"] for r in rows
                                     if r["first_breach_month"] is not None),
            "expected_ending_cash":sum(r["probability"]*r["ending_cash"] for r in rows)}
