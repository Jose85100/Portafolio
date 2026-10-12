"""Correlated venture exit simulation with common market factor."""
from dataclasses import dataclass
from math import exp, isfinite, sqrt
from random import Random

@dataclass(frozen=True)
class Startup:
    name: str
    ticket: float
    failure_probability: float
    log_exit_mean: float
    log_exit_volatility: float

def simulate(starts, scenarios=10000, correlation=0.25, seed=17, alpha=0.95):
    if not starts or scenarios < 1 or not -1e-12 <= correlation <= 1 or not 0 < alpha < 1:
        raise ValueError("invalid simulation setup")
    # One-factor loadings imply nonnegative pairwise correlation.
    if correlation < 0:
        raise ValueError("one-factor model requires nonnegative correlation")
    for x in starts:
        if not x.name or not all(isfinite(v) for v in
                (x.ticket,x.failure_probability,x.log_exit_mean,x.log_exit_volatility)):
            raise ValueError("invalid startup inputs")
        if x.ticket <= 0 or not 0 <= x.failure_probability <= 1 or x.log_exit_volatility < 0:
            raise ValueError("invalid startup economics")
    rng = Random(seed)
    invested = sum(x.ticket for x in starts)
    outcomes = []
    loading, residual = sqrt(correlation), sqrt(1-correlation)
    for _ in range(scenarios):
        common = rng.gauss(0,1)
        proceeds = 0.0
        for company in starts:
            shock = loading*common + residual*rng.gauss(0,1)
            if rng.random() >= company.failure_probability:
                proceeds += company.ticket * exp(
                    company.log_exit_mean + company.log_exit_volatility*shock)
        outcomes.append(proceeds-invested)
    outcomes.sort()
    tail_count = max(1, int((1-alpha)*scenarios))
    return {"initial_capital": invested,
            "expected_profit": sum(outcomes)/scenarios,
            "loss_probability": sum(x < 0 for x in outcomes)/scenarios,
            "var_loss": -outcomes[tail_count-1],
            "expected_shortfall_loss": -sum(outcomes[:tail_count])/tail_count,
            "p05_profit": outcomes[max(0,int(.05*(scenarios-1)))],
            "p95_profit": outcomes[int(.95*(scenarios-1))]}
