"""Segment economics, contribution margins and break-even analysis."""
from dataclasses import dataclass
from math import ceil,isfinite

@dataclass(frozen=True)
class Segment:
    name: str
    customers: int
    price: float
    variable_cost: float
    acquisition_cost: float
    fixed_cost: float
    monthly_churn: float

def analyze(segments):
    if not segments:
        raise ValueError("at least one segment required")
    rows = []
    for s in segments:
        nums=(s.price,s.variable_cost,s.acquisition_cost,s.fixed_cost,s.monthly_churn)
        if not s.name or not isinstance(s.customers,int) or s.customers < 0:
            raise ValueError("invalid segment")
        if any(not isfinite(x) or x < 0 for x in nums) or s.monthly_churn > 1:
            raise ValueError("invalid economic parameter")
        contribution = s.price-s.variable_cost
        operating_profit = s.customers*contribution-s.fixed_cost
        break_even = ceil(s.fixed_cost/contribution) if contribution > 0 else None
        # Geometric lifetime assumes constant monthly churn and contribution.
        ltv = contribution/s.monthly_churn if s.monthly_churn > 0 else None
        rows.append({"segment":s.name,"contribution_per_customer":contribution,
                     "operating_profit":operating_profit,
                     "break_even_customers":break_even,"ltv_before_cac":ltv,
                     "ltv_to_cac":ltv/s.acquisition_cost if ltv is not None and s.acquisition_cost>0 else None})
    return {"segments":rows,"total_operating_profit":sum(x["operating_profit"] for x in rows)}
