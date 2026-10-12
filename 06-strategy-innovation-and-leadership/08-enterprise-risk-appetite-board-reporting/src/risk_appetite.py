"""Risk appetite limits with explicit breach and escalation logic."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class RiskMetric:
    name: str
    observed: float
    limit: float
    warning_ratio: float = .8
    direction: str = "upper"

def assess(metrics):
    if not metrics or len({m.name for m in metrics}) != len(metrics):
        raise ValueError("metrics required with unique names")
    rows = []
    for m in metrics:
        if not m.name or m.direction not in ("upper","lower"):
            raise ValueError("invalid metric")
        if not all(isfinite(x) for x in (m.observed,m.limit,m.warning_ratio)):
            raise ValueError("non-finite input")
        if m.limit <= 0 or not 0 < m.warning_ratio < 1:
            raise ValueError("limits must be positive and warning ratio interior")
        if m.direction == "upper":
            utilization = m.observed/m.limit
        else:
            if m.observed <= 0:
                utilization = float("inf")
            else:
                utilization = m.limit/m.observed
        status = ("breach" if utilization > 1 else
                  "warning" if utilization >= m.warning_ratio else "within_appetite")
        rows.append({"metric":m.name,"utilization":utilization,"status":status,
                     "escalation": "board" if status=="breach" else
                     "risk_committee" if status=="warning" else "none"})
    return {"metrics":rows,"breaches":sum(x["status"]=="breach" for x in rows),
            "warnings":sum(x["status"]=="warning" for x in rows)}
