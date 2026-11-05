"""Finite Beta-Binomial EVSI gate for a synthetic pricing pilot."""
from __future__ import annotations
from dataclasses import dataclass
from math import comb
from typing import Iterable

@dataclass(frozen=True)
class Price:
    name: str
    margin: float
    alpha: float
    beta: float

@dataclass(frozen=True)
class Decision:
    action: str
    value: float


def choose(prices: Iterable[Price]) -> Decision:
    """Risk-neutral expected contribution per eligible customer; zero=close."""
    candidates = [Decision("close", 0.0)]
    candidates += [Decision(p.name, p.margin * (p.alpha / (p.alpha+p.beta))) for p in prices]
    return max(candidates, key=lambda d: (d.value, d.action == "close"))


def predictive_prob(x: int, n: int, a: float, b: float) -> float:
    """Beta-binomial predictive mass; computed by a stable recurrence-free formula."""
    if not (0 <= x <= n and n >= 0 and a > 0 and b > 0):
        raise ValueError("invalid binomial count or beta prior")
    # Integer-count beta function ratio; inputs are small in this experiment.
    from math import lgamma, exp
    logp = (lgamma(n+1)-lgamma(x+1)-lgamma(n-x+1)
            + lgamma(a+x)+lgamma(b+n-x)-lgamma(a+b+n)
            - lgamma(a)-lgamma(b)+lgamma(a+b))
    return exp(logp)


def evaluate(prices: list[Price], n: int, pilot_cost: float) -> dict[str,float|str]:
    """Balanced randomized pilot: n observations per price arm; exact enumeration."""
    if n < 0 or pilot_cost < 0:
        raise ValueError("n and pilot_cost must be nonnegative")
    base = choose(prices)
    if len(prices) != 2:
        raise ValueError("this MVP supports exactly two randomized price arms")
    with_info = 0.0
    mass = 0.0
    for x in range(n+1):
        px = predictive_prob(x,n,prices[0].alpha,prices[0].beta)
        for y in range(n+1):
            py = predictive_prob(y,n,prices[1].alpha,prices[1].beta)
            posterior_prices=[Price(prices[0].name,prices[0].margin,prices[0].alpha+x,prices[0].beta+n-x),
                              Price(prices[1].name,prices[1].margin,prices[1].alpha+y,prices[1].beta+n-y)]
            prob=px*py
            with_info += prob*choose(posterior_prices).value
            mass += prob
    evsi=with_info-base.value
    return {"n_per_arm":n,"pilot_cost":pilot_cost,"baseline_action":base.action,
            "baseline_value":base.value,"expected_value_after_sample":with_info,
            "evsi":evsi,"net_evsi":evsi-pilot_cost,"predictive_mass":mass,
            "decision":"pilot" if evsi>pilot_cost else "launch_now_or_close"}
