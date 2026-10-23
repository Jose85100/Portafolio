"""Exact one-stage beta-binomial decision value; all cash flows use one unit."""
from dataclasses import dataclass
from math import exp, isfinite, lgamma


@dataclass(frozen=True)
class Case:
    alpha: float = 6.0
    beta: float = 4.0
    population: int = 10000
    benefit: float = 10.0
    unit_cost: float = 6.0
    fixed_rollout: float = 0.0
    experiment_fixed: float = 100.0
    experiment_unit: float = 5.0

    def __post_init__(self) -> None:
        values = (self.alpha, self.beta, self.benefit, self.unit_cost,
                  self.fixed_rollout, self.experiment_fixed, self.experiment_unit)
        if not all(isfinite(x) for x in values):
            raise ValueError('finite inputs required')
        if self.alpha <= 0 or self.beta <= 0 or self.benefit <= 0:
            raise ValueError('positive prior and benefit required')
        if not isinstance(self.population, int) or isinstance(self.population, bool) or self.population < 0:
            raise ValueError('population must be nonnegative integer')
        if min(self.unit_cost, self.fixed_rollout, self.experiment_fixed,
               self.experiment_unit) < 0:
            raise ValueError('costs must be nonnegative')

    def payoff(self, probability: float) -> float:
        return self.population * (self.benefit * probability - self.unit_cost) - self.fixed_rollout


def predictive(case: Case, n: int) -> list[float]:
    """P(K=k) from beta-binomial log PMF; normalization counters rounding."""
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        raise ValueError('sample size must be nonnegative integer')
    a, b = case.alpha, case.beta
    log_beta = lgamma(a) + lgamma(b) - lgamma(a + b)
    logs = [lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)
            + lgamma(a + k) + lgamma(b + n - k) - lgamma(a + b + n)
            - log_beta for k in range(n + 1)]
    maximum = max(logs)
    weights = [exp(x - maximum) for x in logs]
    total = sum(weights)
    return [w / total for w in weights]


def evaluate(case: Case, n: int) -> dict[str, float | int]:
    masses = predictive(case, n)
    immediate = max(0.0, case.payoff(case.alpha / (case.alpha + case.beta)))
    future = sum(p * max(0.0, case.payoff((case.alpha + k) /
                 (case.alpha + case.beta + n))) for k, p in enumerate(masses))
    cost = case.experiment_fixed + n * case.experiment_unit if n else 0.0
    return {'n': n, 'evsi': future - immediate, 'experiment_cost': cost,
            'net_value': future - cost, 'immediate_value': immediate,
            'increment': future - immediate - cost}


def choose(case: Case, sizes: list[int]) -> dict[str, float | int | str]:
    if not sizes or 0 not in sizes:
        raise ValueError('candidate set must include no-study option n=0')
    best = max((evaluate(case, n) for n in sorted(set(sizes))),
               key=lambda x: float(x['net_value']))
    action = 'experimentar' if best['n'] else ('escalar' if best['net_value'] > 0 else 'detener')
    return {**best, 'action': action}
