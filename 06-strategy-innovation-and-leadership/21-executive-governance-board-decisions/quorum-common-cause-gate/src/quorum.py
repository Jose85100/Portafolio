"""Exact finite-regime committee availability; no voting or legal conclusions."""
from dataclasses import dataclass
from itertools import product
from math import isfinite,prod
from typing import TypedDict


@dataclass(frozen=True)
class Regime:
    name: str
    weight: float
    attendance: tuple[float,...]


class Outcome(TypedDict):
    available: float
    total_mass: float
    states: int


def validate(regimes: list[Regime], quorum: int, mandatory: tuple[int,...]) -> int:
    if not regimes or not regimes[0].attendance:
        raise ValueError('nonempty regimes and member set required')
    n=len(regimes[0].attendance)
    if n>16 or not isinstance(quorum,int) or isinstance(quorum,bool) or not 1<=quorum<=n:
        raise ValueError('supports 1..16 members and valid integer quorum')
    if len(set(mandatory))!=len(mandatory) or any(not isinstance(i,int) or isinstance(i,bool) or not 0<=i<n for i in mandatory):
        raise ValueError('invalid mandatory member indices')
    if len({r.name for r in regimes})!=len(regimes):
        raise ValueError('unique regime names required')
    for r in regimes:
        if (not r.name or not isfinite(r.weight) or r.weight<=0 or len(r.attendance)!=n
                or not all(isfinite(p) and 0<=p<=1 for p in r.attendance)):
            raise ValueError('finite normalized regime weights and attendance probabilities required')
    if abs(sum(r.weight for r in regimes)-1)>1e-10:
        raise ValueError('regime weights must sum to one')
    return n


def enumerate_states(regimes: list[Regime], quorum: int, mandatory: tuple[int,...]) -> list[dict[str,float|int|str]]:
    n=validate(regimes,quorum,mandatory)
    rows: list[dict[str,float|int|str]]=[]
    for regime in regimes:
        for mask in product((0,1),repeat=n):
            mass=regime.weight*prod(p if present else 1-p for present,p in zip(mask,regime.attendance))
            valid=int(sum(mask)>=quorum and all(mask[i] for i in mandatory))
            rows.append({'regime':regime.name,'mask':''.join(map(str,mask)),'mass':mass,'valid':valid})
    return rows


def exact(regimes: list[Regime], quorum: int, mandatory: tuple[int,...]) -> Outcome:
    rows=enumerate_states(regimes,quorum,mandatory)
    return {'available':sum(float(r['mass'])*int(r['valid']) for r in rows),
            'total_mass':sum(float(r['mass']) for r in rows),'states':len(rows)}


def independent_marginals(regimes: list[Regime], quorum: int, mandatory: tuple[int,...]) -> Outcome:
    n=validate(regimes,quorum,mandatory)
    marginal=tuple(sum(r.weight*r.attendance[i] for r in regimes) for i in range(n))
    return exact([Regime('independent_marginal',1,marginal)],quorum,mandatory)


def add_standbys(regimes: list[Regime], count: int, attendance: float) -> list[Regime]:
    if (not isinstance(count,int) or isinstance(count,bool) or count<0
            or not isfinite(attendance) or not 0<=attendance<=1):
        raise ValueError('nonnegative standby count and probability required')
    return [Regime(r.name,r.weight,r.attendance+(attendance,)*count) for r in regimes]


class Decision(TypedDict):
    standbys: int
    cost: float
    availability: float


def choose(regimes: list[Regime], quorum: int, mandatory: tuple[int,...],
           menu: list[int], standby_attendance: float, unit_cost: float,
           target: float, independent: bool=False) -> Decision:
    if not menu or not isfinite(unit_cost) or unit_cost<0 or not isfinite(target) or not 0<=target<=1:
        raise ValueError('menu, finite nonnegative cost and target [0,1] required')
    measure=independent_marginals if independent else exact
    candidates: list[Decision]=[]
    for count in sorted(set(menu)):
        expanded=add_standbys(regimes,count,standby_attendance)
        probability=measure(expanded,quorum,mandatory)['available']
        if probability>=target-1e-12:
            candidates.append({'standbys':count,'cost':count*unit_cost,'availability':probability})
    if not candidates:
        raise ValueError('no authorized standby plan reaches availability target')
    return min(candidates,key=lambda row:(row['cost'],row['standbys']))
