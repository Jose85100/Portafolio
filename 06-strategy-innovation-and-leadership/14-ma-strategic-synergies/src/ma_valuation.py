"""Incremental M&A valuation with scenario-weighted synergy cash flows."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class AcquisitionScenario:
    name: str
    probability: float
    annual_synergies: tuple[float, ...]
    integration_costs: tuple[float, ...]

def value_transaction(standalone_value, purchase_price, discount_rate, scenarios):
    if not scenarios or any(not isfinite(x) for x in (standalone_value,purchase_price,discount_rate)):
        raise ValueError("invalid transaction")
    if standalone_value<0 or purchase_price<0 or discount_rate<=-1:
        raise ValueError("invalid valuation inputs")
    if abs(sum(s.probability for s in scenarios)-1)>1e-9:
        raise ValueError("scenario probabilities must sum to one")
    results=[]
    for s in scenarios:
        if not s.name or not s.annual_synergies or len(s.annual_synergies)!=len(s.integration_costs):
            raise ValueError("invalid cash flow horizon")
        if not isfinite(s.probability) or s.probability<0:
            raise ValueError("invalid probability")
        if any(not isfinite(x) for x in (*s.annual_synergies,*s.integration_costs)):
            raise ValueError("nonfinite cash flow")
        synergy_npv=sum((synergy-cost)/(1+discount_rate)**t
                        for t,(synergy,cost) in enumerate(zip(s.annual_synergies,s.integration_costs),1))
        deal_npv=standalone_value+synergy_npv-purchase_price
        results.append({"scenario":s.name,"probability":s.probability,
                        "synergy_npv":synergy_npv,"deal_npv":deal_npv})
    return {"scenarios":results,
            "expected_deal_npv":sum(x["probability"]*x["deal_npv"] for x in results),
            "probability_of_value_destruction":sum(x["probability"] for x in results if x["deal_npv"]<0)}
