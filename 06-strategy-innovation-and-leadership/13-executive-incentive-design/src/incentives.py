"""Risk-adjusted variable compensation with malus and deferral."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class ExecutiveScore:
    name: str
    base_salary: float
    target_bonus_ratio: float
    financial_score: float
    customer_score: float
    risk_loss_ratio: float
    compliance_breach: bool = False

def calculate(scores, financial_weight=.6, defer_ratio=.4, risk_penalty=2.0):
    if not scores or not all(isfinite(v) for v in (financial_weight,defer_ratio,risk_penalty)):
        raise ValueError("invalid policy")
    if not 0<=financial_weight<=1 or not 0<=defer_ratio<=1 or risk_penalty<0:
        raise ValueError("invalid policy weights")
    rows=[]
    for s in scores:
        nums=(s.base_salary,s.target_bonus_ratio,s.financial_score,
              s.customer_score,s.risk_loss_ratio)
        if not s.name or any(not isfinite(v) or v<0 for v in nums):
            raise ValueError("invalid executive score")
        if s.financial_score>2 or s.customer_score>2 or s.risk_loss_ratio>1:
            raise ValueError("scores outside allowed range")
        achievement=financial_weight*s.financial_score+(1-financial_weight)*s.customer_score
        risk_factor=max(0,1-risk_penalty*s.risk_loss_ratio)
        bonus=0.0 if s.compliance_breach else s.base_salary*s.target_bonus_ratio*achievement*risk_factor
        rows.append({"name":s.name,"bonus":bonus,"paid_now":bonus*(1-defer_ratio),
                     "deferred":bonus*defer_ratio,"risk_factor":risk_factor})
    return {"executives":rows,"total_bonus":sum(x["bonus"] for x in rows),
            "total_deferred":sum(x["deferred"] for x in rows)}
