"""Inverse propensity and self-normalized policy evaluation for logged bandit data."""
from math import isfinite

def evaluate(rows, target_policy):
    if not rows: raise ValueError("empty observations")
    weights=[];outcomes=[]
    for r in rows:
        p=r["propensity"];target=target_policy(r["context"],r["action"])
        if not 0<p<=1 or not 0<=target<=1 or not isfinite(r["reward"]): raise ValueError("invalid propensity/reward")
        weights.append(target/p);outcomes.append(r["reward"])
    ips=sum(w*y for w,y in zip(weights,outcomes))/len(rows)
    snips=sum(w*y for w,y in zip(weights,outcomes))/sum(weights) if sum(weights)>0 else float("nan")
    ess=sum(weights)**2/sum(w*w for w in weights) if any(weights) else 0.0
    return {"ips":ips,"snips":snips,"effective_sample_size":ess,"n":len(rows)}
