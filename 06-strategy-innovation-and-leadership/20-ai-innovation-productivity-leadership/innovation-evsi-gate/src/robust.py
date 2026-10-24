"""Common terminal policy evaluated under alternative priors and delay costs."""
from dataclasses import replace
from math import exp, isfinite
from typing import TypedDict
from src.evsi import Case, predictive


class Design(TypedDict):
    n: int
    objective: float
    scenario_values: list[float]
    worst_value: float


class Selection(TypedDict):
    selected: Design
    designs: list[Design]
    robust: bool


def policy_value(case: Case, n: int, policy_prior: tuple[float, float],
                 daily_discount: float = 0.0, observations_per_day: float = 10.0,
                 robust_terminal: tuple[tuple[float, float], ...] = ()) -> float:
    """Prior-predictive payoff of ONE policy, not an oracle per scenario.

    policy_prior fixes the terminal decision; robust_terminal substitutes a
    worst-posterior-mean threshold, shared across every evaluation scenario.
    Pilot cost is paid now; all future deployment net cash is discounted.
    """
    if (not isfinite(daily_discount) or daily_discount < 0
            or not isfinite(observations_per_day) or observations_per_day <= 0):
        raise ValueError('finite nonnegative discount and positive rate required')
    priors = robust_terminal or (policy_prior,)
    for a, b in priors:
        replace(case, alpha=a, beta=b)  # reuse validated prior contract
    masses = predictive(case, n)
    deployment = 0.0
    for k, mass in enumerate(masses):
        means = [(a + k) / (a + b + n) for a, b in priors]
        deploy = min(case.payoff(mean) for mean in means) > 0
        actual_mean = (case.alpha + k) / (case.alpha + case.beta + n)
        deployment += mass * deploy * case.payoff(actual_mean)
    cost = case.experiment_fixed + n * case.experiment_unit if n else 0.0
    return exp(-daily_discount * n / observations_per_day) * deployment - cost


def select(case: Case, sizes: list[int], priors: tuple[tuple[float, float], ...],
           daily_discount: float = 0.0, observations_per_day: float = 10.0,
           robust: bool = True) -> Selection:
    if not priors or not sizes or 0 not in sizes:
        raise ValueError('nonempty prior set and no-study candidate required')
    terminal = priors if robust else ()
    nominal = (case.alpha, case.beta)
    designs: list[Design] = []
    for n in sorted(set(sizes)):
        values = [policy_value(replace(case, alpha=a, beta=b), n, nominal,
                               daily_discount, observations_per_day, terminal)
                  for a, b in priors]
        objective = min(values) if robust else policy_value(case, n, nominal,
                                  daily_discount, observations_per_day)
        designs.append({'n': n, 'objective': objective, 'scenario_values': values,
                        'worst_value': min(values)})
    best = max(designs, key=lambda row: float(row['objective']))
    return {'selected': best, 'designs': designs, 'robust': robust}
