"""Cumulative extension: sharp two-reserve dependence bounds, fixed event of Oct29.

Risk-lead attendance is still independent of the reserve pair conditional on
regime. Main three members are present in normal, absent in disruption.
"""
from dataclasses import dataclass
from math import isfinite,sqrt
from typing import TypedDict
from src.quorum import Regime,exact


@dataclass(frozen=True)
class ReservePlan:
    name: str
    q1: float
    q2: float
    cost: float

    def __post_init__(self) -> None:
        if (not self.name or not all(isfinite(v) for v in (self.q1,self.q2,self.cost))
                or not 0<=self.q1<=1 or not 0<=self.q2<=1 or self.cost<0):
            raise ValueError('finite reserve attendance probabilities and nonnegative cost required')


class Bounds(TypedDict):
    lower_joint: float
    independent_joint: float
    upper_joint: float
    lower_availability: float
    nominal_availability: float
    upper_availability: float


def bounds(plan: ReservePlan, shock: float=.2, risk: float=.95) -> Bounds:
    if not all(isfinite(x) and 0<=x<=1 for x in (shock,risk)):
        raise ValueError('shock weight and risk-role attendance must lie in [0,1]')
    lower=max(0.0,plan.q1+plan.q2-1)
    nominal=plan.q1*plan.q2
    upper=min(plan.q1,plan.q2)
    return {'lower_joint':lower,'independent_joint':nominal,'upper_joint':upper,
            'lower_availability':risk*(1-shock+shock*lower),
            'nominal_availability':risk*(1-shock+shock*nominal),
            'upper_availability':risk*(1-shock+shock*upper)}


def coupling(plan: ReservePlan, joint: float) -> tuple[float,float,float,float]:
    b=bounds(plan)
    if not isfinite(joint) or joint<b['lower_joint']-1e-12 or joint>b['upper_joint']+1e-12:
        raise ValueError('joint mass violates marginal feasibility')
    # Order 00,01,10,11. Nonnegativity yields the sharp Frechet interval.
    return (1-plan.q1-plan.q2+joint,plan.q2-joint,plan.q1-joint,joint)


def nominal_existing_engine(plan: ReservePlan, shock: float=.2, risk: float=.95) -> float:
    bounds(plan,shock,risk)
    regimes=[]
    if shock<1:
        regimes.append(Regime('normal',1-shock,(risk,1,1,1,.9,.9)))
    if shock>0:
        regimes.append(Regime('shock',shock,(risk,0,0,0,plan.q1,plan.q2)))
    return exact(regimes,3,(0,))['available']


class Choice(TypedDict):
    name: str
    cost: float
    lower_availability: float
    nominal_availability: float
    upper_availability: float


def choose_plan(plans: list[ReservePlan], target: float=.85, shock: float=.2,
                risk: float=.95, robust: bool=True) -> Choice:
    if not plans or len({p.name for p in plans})!=len(plans) or not isfinite(target) or not 0<=target<=1:
        raise ValueError('unique nonempty plans and target [0,1] required')
    candidates: list[Choice]=[]
    for plan in plans:
        b=bounds(plan,shock,risk)
        criterion=b['lower_availability'] if robust else b['nominal_availability']
        if criterion>=target-1e-12:
            candidates.append({'name':plan.name,'cost':plan.cost,
                               'lower_availability':b['lower_availability'],
                               'nominal_availability':b['nominal_availability'],
                               'upper_availability':b['upper_availability']})
    if not candidates:
        raise ValueError('no plan in menu reaches the specified dependence-aware criterion')
    return min(candidates,key=lambda c:(c['cost'],c['name']))


def symmetric_threshold(target: float=.85, shock: float=.2, risk: float=.95) -> tuple[float,float]:
    if (not all(isfinite(v) for v in (target,shock,risk)) or not 0<=target<=1
            or not 0<shock<=1 or not 0<risk<=1):
        raise ValueError('threshold calculation needs positive shock/risk and valid target')
    required_joint=(target/risk-(1-shock))/shock
    if required_joint>1+1e-12:
        raise ValueError('target exceeds mandatory-role upper bound')
    if required_joint<=0:
        return 0.0,0.0
    return sqrt(required_joint),(1+required_joint)/2
