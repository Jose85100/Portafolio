"""Environment-wise risk and invariance diagnostics; not a causal identification test."""

def environment_risk(records,predictor):
    by={}
    for r in records:
        env=r["environment"];error=(r["target"]-predictor(r["features"]))**2
        by.setdefault(env,[]).append(error)
    if len(by)<2: raise ValueError("at least two environments required")
    risks={k:sum(v)/len(v) for k,v in by.items()}
    return {"risk_by_environment":risks,"risk_gap":max(risks.values())-min(risks.values()),"worst_risk":max(risks.values())}
