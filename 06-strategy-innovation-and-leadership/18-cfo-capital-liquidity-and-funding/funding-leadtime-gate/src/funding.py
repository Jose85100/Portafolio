"""One committed draw with observable-cash trigger and deterministic lead time."""
from dataclasses import dataclass
from math import isfinite
from typing import TypedDict


@dataclass(frozen=True)
class Facility:
    initial_cash: float = 8.0
    amount: float = 8.0
    request_fee: float = 0.5
    interest_per_period: float = 0.02
    lead: int = 2
    floor: float = 0.0

    def __post_init__(self) -> None:
        values=(self.initial_cash,self.amount,self.request_fee,self.interest_per_period,self.floor)
        if not all(isfinite(v) for v in values) or min(values[:4]) < 0:
            raise ValueError('finite cash/funding/costs and nonnegative economics required')
        if not isinstance(self.lead,int) or isinstance(self.lead,bool) or self.lead < 0:
            raise ValueError('lead must be nonnegative integer')


class Result(TypedDict):
    request_period: int | None
    funding_period: int | None
    first_breach: int | None
    cash: list[float]
    debt: list[float]
    observed_cash: list[float]
    costs: float
    reconciliation_error: float


def simulate(flows: list[float], threshold: float | None, facility: Facility) -> Result:
    if not flows or not all(isfinite(v) for v in flows) or (threshold is not None and not isfinite(threshold)):
        raise ValueError('finite nonempty net flows and threshold required')
    cash,debt,costs=facility.initial_cash,0.0,0.0
    requested: int | None=None
    funded: int | None=None
    first: int | None=-1 if cash < facility.floor else None
    cash_path,debt_path,observed=[],[],[]
    cumulative=0.0
    error=0.0
    for t,net_flow in enumerate(flows):
        if requested is not None and t == requested+facility.lead:
            cash+=facility.amount
            debt+=facility.amount
            funded=t
        observed.append(cash)
        # Only current cash, fixed horizon and contract are used to request.
        if requested is None and threshold is not None and cash <= threshold and t+facility.lead < len(flows):
            requested=t
            cash-=facility.request_fee
            costs+=facility.request_fee
            if facility.lead == 0:
                cash+=facility.amount
                debt+=facility.amount
                funded=t
        if first is None and cash < facility.floor:
            first=t
        interest=debt*facility.interest_per_period
        cash+=net_flow-interest
        costs+=interest
        cumulative+=net_flow
        if first is None and cash < facility.floor:
            first=t
        cash_path.append(cash)
        debt_path.append(debt)
        error=max(error,abs((cash-debt)-(facility.initial_cash+cumulative-costs)))
    return {'request_period':requested,'funding_period':funded,'first_breach':first,
            'cash':cash_path,'debt':debt_path,'observed_cash':observed,
            'costs':costs,'reconciliation_error':error}


class Score(TypedDict):
    threshold: float | None
    breach_probability: float
    expected_cost: float
    outcomes: list[Result]


def score(flows: list[list[float]], weights: list[float], threshold: float | None, facility: Facility) -> Score:
    if (not flows or len(flows)!=len(weights) or len({len(f) for f in flows})!=1
            or not all(isfinite(w) and w>0 for w in weights) or abs(sum(weights)-1)>1e-10):
        raise ValueError('same horizon and normalized positive scenario probabilities required')
    results=[simulate(path,threshold,facility) for path in flows]
    return {'threshold':threshold,
            'breach_probability':sum(w for w,r in zip(weights,results) if r['first_breach'] is not None),
            'expected_cost':sum(w*r['costs'] for w,r in zip(weights,results)), 'outcomes':results}


def choose(flows: list[list[float]], weights: list[float], thresholds: list[float | None],
           facility: Facility, max_breach: float) -> Score:
    if not thresholds or not isfinite(max_breach) or not 0<=max_breach<=1:
        raise ValueError('finite risk budget in [0,1] and menu required')
    candidates=[score(flows,weights,h,facility) for h in thresholds]
    acceptable=[c for c in candidates if c['breach_probability']<=max_breach+1e-12]
    if not acceptable:
        raise ValueError('no feasible threshold in menu; redesign funding/initial buffer')
    return min(acceptable,key=lambda c:c['expected_cost'])
