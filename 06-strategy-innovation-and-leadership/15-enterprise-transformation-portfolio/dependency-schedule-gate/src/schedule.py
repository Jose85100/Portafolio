"""Exact small optional-project schedules with completion prerequisites."""
from dataclasses import dataclass
from itertools import product
from math import isfinite, prod
from typing import TypedDict


@dataclass(frozen=True)
class Job:
    name: str
    cost: float
    benefit: float
    duration: int
    people: int
    dependencies: tuple[str, ...] = ()


class Outcome(TypedDict):
    starts: dict[str, int]
    npv: float
    checked: int


def validate(jobs: list[Job], budgets: list[float], capacity: int, discount: float) -> None:
    if (not jobs or len(jobs) > 8 or not budgets
            or not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 0
            or not isfinite(discount) or discount < 0
            or not all(isfinite(b) and b >= 0 for b in budgets)):
        raise ValueError('supports 1..8 jobs, finite budgets, nonnegative capacity/discount')
    names = {j.name for j in jobs}
    if len(names) != len(jobs):
        raise ValueError('duplicate names')
    for j in jobs:
        if (not j.name or not isfinite(j.cost) or j.cost < 0 or not isfinite(j.benefit)
                or not isinstance(j.duration, int) or isinstance(j.duration, bool) or j.duration <= 0
                or not isinstance(j.people, int) or isinstance(j.people, bool) or j.people <= 0
                or any(d not in names or d == j.name for d in j.dependencies)):
            raise ValueError('invalid job')
    pending = {j.name: set(j.dependencies) for j in jobs}
    while pending:
        ready = [name for name, deps in pending.items() if not deps]
        if not ready:
            raise ValueError('cyclic dependencies')
        for name in ready:
            del pending[name]
        for deps in pending.values():
            deps.difference_update(ready)


def feasible(jobs: list[Job], starts: dict[str, int], budgets: list[float], capacity: int) -> bool:
    lookup = {j.name: j for j in jobs}
    if any(name not in lookup for name in starts):
        return False
    horizon = len(budgets)
    for name, start in starts.items():
        job = lookup[name]
        if (not isinstance(start, int) or isinstance(start, bool) or start < 0
                or start+job.duration > horizon):
            return False
        if any(dep not in starts or starts[dep]+lookup[dep].duration > start for dep in job.dependencies):
            return False
    for t in range(horizon):
        if sum(lookup[n].cost for n,s in starts.items() if s == t) > budgets[t]+1e-10:
            return False
        if sum(lookup[n].people for n,s in starts.items() if s <= t < s+lookup[n].duration) > capacity:
            return False
    return True


def value(jobs: list[Job], starts: dict[str, int], discount: float) -> float:
    return sum(j.benefit/(1+discount)**(starts[j.name]+j.duration)
               -j.cost/(1+discount)**starts[j.name] for j in jobs if j.name in starts)


def exact(jobs: list[Job], budgets: list[float], capacity: int, discount: float) -> Outcome:
    validate(jobs, budgets, capacity, discount)
    choices = [list(range(-1, max(-1, len(budgets)-j.duration)+1)) for j in jobs]
    if prod(len(c) for c in choices) > 2000000:
        raise ValueError('candidate count exceeds 2 million safety limit')
    best: Outcome = {'starts': {}, 'npv': 0.0, 'checked': 0}
    for dates in product(*choices):
        best['checked'] += 1
        starts = {j.name:t for j,t in zip(jobs,dates) if t >= 0}
        if feasible(jobs, starts, budgets, capacity):
            npv = value(jobs, starts, discount)
            if npv > best['npv']+1e-10:
                best['npv'], best['starts'] = npv, starts
    return best


def greedy(jobs: list[Job], budgets: list[float], capacity: int, discount: float) -> Outcome:
    """Feasible serial priority baseline; indirect prerequisite value is ignored."""
    validate(jobs, budgets, capacity, discount)
    starts: dict[str,int] = {}
    needed = {dep for j in jobs for dep in j.dependencies}
    candidates = [j for j in jobs if j.benefit > j.cost or j.name in needed]
    order = sorted(candidates, key=lambda j: (-(j.benefit-j.cost)/max(j.cost,1e-12),j.name))
    for t in range(len(budgets)):
        for job in order:
            if job.name not in starts:
                candidate = {**starts, job.name:t}
                if feasible(jobs, candidate, budgets, capacity):
                    starts = candidate
    npv = value(jobs, starts, discount)
    return {'starts': starts if npv > 0 else {}, 'npv': max(0.0,npv), 'checked': len(jobs)*len(budgets)}
