"""Exact beta-binomial EVSI with pilot delay and finite horizon."""
from __future__ import annotations
from dataclasses import dataclass
from math import exp, lgamma
import json
from pathlib import Path

@dataclass(frozen=True)
class Arm:
    alpha: float
    beta: float
    margin: float
    price: float

def lbeta(a: float, b: float) -> float:
    return lgamma(a) + lgamma(b) - lgamma(a+b)

def predictive(k: int, n: int, a: float, b: float) -> float:
    if not (a > 0 and b > 0 and 0 <= k <= n):
        raise ValueError("invalid beta-binomial parameters")
    log_choose=lgamma(n+1)-lgamma(k+1)-lgamma(n-k+1)
    return exp(log_choose+lbeta(k+a,n-k+b)-lbeta(a,b))

def expected_margin(arm: Arm) -> float:
    return arm.margin*arm.alpha/(arm.alpha+arm.beta)

def analyze(a: Arm,b: Arm,n: int,horizon: int,delay: int,pilot_cost: float) -> dict:
    if n < 0 or horizon < 1 or delay < 0 or delay > horizon or pilot_cost < 0:
        raise ValueError("invalid experiment design")
    base=max(expected_margin(a),expected_margin(b))*horizon
    post=0.0
    mass=0.0
    for ka in range(n+1):
        pa=predictive(ka,n,a.alpha,a.beta)
        for kb in range(n+1):
            p=pa*predictive(kb,n,b.alpha,b.beta)
            ma=a.margin*(a.alpha+ka)/(a.alpha+a.beta+n)
            mb=b.margin*(b.alpha+kb)/(b.alpha+b.beta+n)
            post+=p*max(ma,mb)
            mass+=p
    pilot=(horizon-delay)*post-pilot_cost
    return {"immediate_value":base,"pilot_value":pilot,"net_gain":pilot-base,
            "predictive_mass":mass,"decision":"pilot" if pilot>base else "immediate",
            "posterior_best_margin":post,"delay":delay,"horizon":horizon}

def main() -> None:
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="results/result.json")
    args=p.parse_args()
    result=analyze(Arm(11,9,10,20),Arm(9,11,12,24),10,100,5,2)
    path=Path(args.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":
    main()
