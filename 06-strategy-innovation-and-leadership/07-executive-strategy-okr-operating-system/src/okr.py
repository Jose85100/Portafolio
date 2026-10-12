"""Deterministic weighted OKR dashboard with accountability flags."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class KeyResult:
    objective: str
    owner: str
    baseline: float
    target: float
    actual: float
    weight: float
    direction: str = "increase"

def evaluate(results, alert_threshold=.7):
    if not results or not 0 <= alert_threshold <= 1:
        raise ValueError("invalid dashboard")
    rows = []
    total_weight = 0.0
    weighted_progress = 0.0
    for r in results:
        if not r.objective or not r.owner or r.direction not in ("increase","decrease"):
            raise ValueError("invalid metadata")
        if not all(isfinite(v) for v in (r.baseline,r.target,r.actual,r.weight)) or r.weight <= 0:
            raise ValueError("invalid numeric inputs")
        improvement = (r.target-r.baseline) if r.direction=="increase" else (r.baseline-r.target)
        achieved = (r.actual-r.baseline) if r.direction=="increase" else (r.baseline-r.actual)
        if improvement <= 0:
            raise ValueError("target must improve baseline")
        progress = max(0.0,min(1.0,achieved/improvement))
        rows.append({"objective":r.objective,"owner":r.owner,"progress":progress,
                     "status":"on_track" if progress >= alert_threshold else "attention"})
        total_weight += r.weight
        weighted_progress += progress*r.weight
    return {"overall_progress":weighted_progress/total_weight,"key_results":rows,
            "attention_count":sum(x["status"]=="attention" for x in rows)}
