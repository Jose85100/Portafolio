"""Exact portfolio choice with budget, delivery capacity and prerequisites."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Program:
    name: str
    cost: int
    people: int
    value: float
    prerequisites: tuple[str,...] = ()

def select(programs, budget, people_capacity):
    if not isinstance(budget,int) or not isinstance(people_capacity,int) or budget<0 or people_capacity<0:
        raise ValueError("invalid capacities")
    if not 1<=len(programs)<=22 or len({p.name for p in programs})!=len(programs):
        raise ValueError("invalid programs")
    names={p.name for p in programs}
    for p in programs:
        if not p.name or not isinstance(p.cost,int) or not isinstance(p.people,int):
            raise ValueError("invalid program fields")
        if p.cost<0 or p.people<0 or not isfinite(p.value):
            raise ValueError("invalid economics")
        if any(d not in names or d==p.name for d in p.prerequisites):
            raise ValueError("invalid prerequisite")
    best_value,best_cost,best_people,best=0.0,0,0,()
    for mask in range(1<<len(programs)):
        chosen=[p for i,p in enumerate(programs) if mask & (1<<i)]
        chosen_names={p.name for p in chosen}
        if any(not set(p.prerequisites).issubset(chosen_names) for p in chosen):
            continue
        cost=sum(p.cost for p in chosen)
        people=sum(p.people for p in chosen)
        if cost>budget or people>people_capacity:
            continue
        value=sum(p.value for p in chosen)-cost
        if value>best_value+1e-10:
            best_value,best_cost,best_people,best=value,cost,people,tuple(sorted(chosen_names))
    return {"selected":best,"net_value":best_value,"cost":best_cost,
            "people_used":best_people,"budget_left":budget-best_cost,
            "people_left":people_capacity-best_people}
