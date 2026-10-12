"""Integrated operating plan: revenue, EBIT, tax, investment and cash."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Scenario:
    name: str
    probability: float
    growth: tuple[float, ...]
    ebit_margin: tuple[float, ...]
    capex_ratio: tuple[float, ...]
    working_capital_ratio: float

def forecast(initial_revenue, initial_cash, tax_rate, scenarios):
    if not scenarios or not all(isfinite(x) for x in (initial_revenue, initial_cash, tax_rate)):
        raise ValueError("invalid initial inputs")
    if initial_revenue <= 0 or initial_cash < 0 or not 0 <= tax_rate <= 1:
        raise ValueError("invalid financial parameters")
    if abs(sum(s.probability for s in scenarios)-1) > 1e-9:
        raise ValueError("scenario probabilities must sum to one")
    paths=[]
    for s in scenarios:
        n=len(s.growth)
        if not s.name or not 1 <= n <= 30 or len(s.ebit_margin)!=n or len(s.capex_ratio)!=n:
            raise ValueError("inconsistent planning horizon")
        nums=(s.probability,s.working_capital_ratio,*s.growth,*s.ebit_margin,*s.capex_ratio)
        if any(not isfinite(x) for x in nums) or s.probability<0 or not 0<=s.working_capital_ratio<=1:
            raise ValueError("invalid scenario")
        if any(g<=-1 for g in s.growth) or any(not 0<=m<=1 for m in s.ebit_margin):
            raise ValueError("invalid growth or margin")
        if any(not 0<=c<=1 for c in s.capex_ratio):
            raise ValueError("invalid capex ratio")
        revenue=initial_revenue
        cash=initial_cash
        rows=[]
        for year,(growth,margin,capex_ratio) in enumerate(zip(s.growth,s.ebit_margin,s.capex_ratio),1):
            previous=revenue
            revenue*=1+growth
            ebit=revenue*margin
            tax=max(0,ebit)*tax_rate
            capex=revenue*capex_ratio
            delta_wc=(revenue-previous)*s.working_capital_ratio
            free_cash_flow=ebit-tax-capex-delta_wc
            cash+=free_cash_flow
            rows.append({"year":year,"revenue":revenue,"ebit":ebit,
                         "free_cash_flow":free_cash_flow,"ending_cash":cash})
        paths.append({"name":s.name,"probability":s.probability,"years":rows})
    if len({len(p["years"]) for p in paths})!=1:
        raise ValueError("scenarios must share a horizon")
    return {"scenarios":paths,"expected_terminal_cash":sum(
        p["probability"]*p["years"][-1]["ending_cash"] for p in paths)}
