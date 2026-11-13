"""Exact beta-binomial EVSI with pilot delay and finite horizon."""
from __future__ import annotations

import json
from dataclasses import dataclass
from math import exp, fsum, isfinite, lgamma
from pathlib import Path


@dataclass(frozen=True)
class Arm:
    alpha: float
    beta: float
    margin: float

    def __post_init__(self) -> None:
        if not all(isfinite(v) for v in (self.alpha, self.beta, self.margin)):
            raise ValueError("arm fields must be finite")
        if self.alpha <= 0 or self.beta <= 0 or self.margin < 0:
            raise ValueError("prior shapes must be positive and contribution margin nonnegative")

def lbeta(a: float, b: float) -> float:
    return lgamma(a) + lgamma(b) - lgamma(a+b)

def predictive(k: int, n: int, a: float, b: float) -> float:
    if not (n >= 0 and a > 0 and b > 0 and 0 <= k <= n):
        raise ValueError("invalid beta-binomial parameters")
    log_choose=lgamma(n+1)-lgamma(k+1)-lgamma(n-k+1)
    return exp(log_choose+lbeta(k+a,n-k+b)-lbeta(a,b))

def expected_margin(arm: Arm) -> float:
    return arm.margin*arm.alpha/(arm.alpha+arm.beta)

def analyze(a: Arm, b: Arm, n: int, horizon: int, delay: int, pilot_cost: float) -> dict[str, float | int | str]:
    if (not isinstance(n, int) or isinstance(n, bool) or n < 0
            or not isinstance(horizon, int) or isinstance(horizon, bool) or horizon < 1
            or not isinstance(delay, int) or isinstance(delay, bool) or delay < 0 or delay > horizon
            or not isfinite(pilot_cost) or pilot_cost < 0):
        raise ValueError("invalid experiment design")
    base=max(expected_margin(a),expected_margin(b))*horizon
    payoffs: list[float] = []
    probabilities: list[float] = []
    for ka in range(n+1):
        pa=predictive(ka,n,a.alpha,a.beta)
        for kb in range(n+1):
            p=pa*predictive(kb,n,b.alpha,b.beta)
            ma=a.margin*(a.alpha+ka)/(a.alpha+a.beta+n)
            mb=b.margin*(b.alpha+kb)/(b.alpha+b.beta+n)
            payoffs.append(p*max(ma,mb))
            probabilities.append(p)
    post=fsum(payoffs)
    mass=fsum(probabilities)
    # EVSI should be nonnegative when the pilot and immediate option share a horizon.
    evsi=horizon*post-base
    pilot=(horizon-delay)*post-pilot_cost
    no_delay_pilot=horizon*post-pilot_cost
    return {"immediate_value":base,"pilot_value":pilot,"net_gain":pilot-base,
            "no_delay_pilot_value":no_delay_pilot,"evsi":evsi,
            "delay_cost_vs_no_delay":delay*post,
            "predictive_mass":mass,"decision":"pilot" if pilot>base else "immediate",
            "posterior_best_margin":post,"delay":delay,"horizon":horizon,
            "roundoff_mass_error":mass-1.0,
            "evsi_negative_roundoff":evsi < 0 and evsi >= -1e-10*max(1.0, abs(base))}

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
