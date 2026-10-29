"""Finite-action incentive audit for a contingent deferred volume bonus."""
from dataclasses import dataclass
from math import isfinite
from typing import TypedDict


@dataclass(frozen=True)
class Action:
    name: str
    volume: float
    failure_probability: float
    success_profit: float
    failure_profit: float
    effort_cost: float

    def __post_init__(self) -> None:
        values=(self.volume,self.failure_probability,self.success_profit,self.failure_profit,self.effort_cost)
        if (not self.name or self.name=='OUTSIDE' or not all(isfinite(x) for x in values) or self.volume<0
                or self.effort_cost<0 or not 0<=self.failure_probability<=1):
            raise ValueError('finite action economics and valid probability required')


class Economics(TypedDict):
    name: str
    success_bonus: float
    failure_bonus: float
    expected_bonus: float
    manager_utility: float
    gross_profit: float
    net_profit: float


def evaluate(action: Action, rate: float, deferred: float) -> Economics:
    if not isfinite(rate) or rate<0 or not isfinite(deferred) or not 0<=deferred<=1:
        raise ValueError('finite nonnegative bonus rate and deferral in [0,1] required')
    bonus=rate*action.volume
    expected=bonus*(1-deferred*action.failure_probability)
    gross=(1-action.failure_probability)*action.success_profit+action.failure_probability*action.failure_profit
    return {'name':action.name,'success_bonus':bonus,'failure_bonus':bonus*(1-deferred),
            'expected_bonus':expected,'manager_utility':expected-action.effort_cost,
            'gross_profit':gross,'net_profit':gross-expected}


def response(actions: list[Action], rate: float, deferred: float, outside: float=0) -> Economics:
    if not actions or len({a.name for a in actions})!=len(actions) or not isfinite(outside):
        raise ValueError('nonempty unique action set and finite outside option required')
    rows=[evaluate(a,rate,deferred) for a in actions]
    rows.append({'name':'OUTSIDE','success_bonus':0,'failure_bonus':0,'expected_bonus':0,
                 'manager_utility':outside,'gross_profit':0,'net_profit':0})
    best=max(r['manager_utility'] for r in rows)
    # Principal-adverse tie rule: do not claim implementation on an optimistic tie.
    return min((r for r in rows if r['manager_utility']>=best-1e-10),key=lambda r:r['net_profit'])


class Contract(TypedDict):
    deferred: float
    target: Economics
    ic_margin: float
    participation_surplus: float
    implemented: str


def audit(actions: list[Action], target: str, rate: float, deferred: float, outside: float=0) -> Contract:
    actual=response(actions,rate,deferred,outside)
    economics=[evaluate(a,rate,deferred) for a in actions]
    matches=[r for r in economics if r['name']==target]
    if not matches:
        raise ValueError('target must be present in action set')
    chosen=matches[0]
    alternatives=[r['manager_utility'] for r in economics if r['name']!=target]
    margin=chosen['manager_utility']-max(alternatives,default=outside)
    return {'deferred':deferred,'target':chosen,'ic_margin':margin,
            'participation_surplus':chosen['manager_utility']-outside,'implemented':actual['name']}


def design(actions: list[Action], target: str, rate: float, menu: list[float],
           required_margin: float=.05, outside: float=0) -> Contract:
    if not menu or not isfinite(required_margin) or required_margin<=0:
        raise ValueError('nonempty menu and positive finite IC margin required')
    candidates=[audit(actions,target,rate,f,outside) for f in sorted(set(menu))]
    feasible=[c for c in candidates if c['ic_margin']>=required_margin-1e-10
              and c['participation_surplus']>=-1e-10 and c['implemented']==target
              and c['target']['net_profit']>=0]
    if not feasible:
        raise ValueError('target not implementable under supplied bounded contract menu')
    # Governance objective: least restrictive deferral, not maximum principal profit.
    return feasible[0]
