"""Simultaneous one-sided bounds for a predeclared synthetic plan menu.

These bounds require independent, identically distributed Bernoulli sessions
within each plan. They do not turn designed counts into empirical evidence.
"""
from dataclasses import dataclass
from math import comb, isfinite, log, sqrt
from collections.abc import Callable
from typing import TypedDict

from scipy.stats import beta, binom  # type: ignore[import-untyped]

BoundMethod = Callable[[int, int, float], float]


class BoundRow(TypedDict):
    plan: str
    cost: float
    successes: int
    trials: int
    estimate: float
    alpha_each: float
    lower: float


@dataclass(frozen=True)
class PlanCount:
    name: str
    cost: float
    successes: int
    trials: int

    def __post_init__(self) -> None:
        if not self.name or not isfinite(self.cost) or self.cost < 0:
            raise ValueError("plan requires a name and finite nonnegative cost")
        if isinstance(self.successes, bool) or isinstance(self.trials, bool):
            raise ValueError("successes and trials must be integers")
        if not isinstance(self.successes, int) or not isinstance(self.trials, int):
            raise ValueError("successes and trials must be integers")
        if self.trials <= 0 or not 0 <= self.successes <= self.trials:
            raise ValueError("require trials > 0 and 0 <= successes <= trials")


def _validate_alpha(alpha: float) -> None:
    if not isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be finite and strictly between 0 and 1")


def clopper_pearson_lower(successes: int, trials: int, alpha: float) -> float:
    """Exact one-sided binomial lower confidence limit (CP, numerical beta quantile)."""
    _validate_counts(successes, trials)
    _validate_alpha(alpha)
    if successes == 0:
        return 0.0
    return float(beta.ppf(alpha, successes, trials - successes + 1))


def hoeffding_lower(successes: int, trials: int, alpha: float) -> float:
    """One-sided Hoeffding lower bound; deliberately not clipped to [0, 1]."""
    _validate_counts(successes, trials)
    _validate_alpha(alpha)
    return successes / trials - sqrt(log(1 / alpha) / (2 * trials))


def _validate_counts(successes: int, trials: int) -> None:
    if isinstance(successes, bool) or isinstance(trials, bool):
        raise ValueError("successes and trials must be integers")
    if not isinstance(successes, int) or not isinstance(trials, int):
        raise ValueError("successes and trials must be integers")
    if trials <= 0 or not 0 <= successes <= trials:
        raise ValueError("require trials > 0 and 0 <= successes <= trials")


def exact_lower_coverage(trials: int, probability: float, alpha: float, method: str) -> float:
    """Exact coverage P_p(L(X) <= p), summed over all binomial outcomes."""
    if not isinstance(trials, int) or isinstance(trials, bool) or trials <= 0:
        raise ValueError("trials must be a positive integer")
    if not isfinite(probability) or not 0 <= probability <= 1:
        raise ValueError("probability must be finite and in [0, 1]")
    _validate_alpha(alpha)
    bound = _bound_for(method)
    included = [x for x in range(trials + 1)
                if bound(x, trials, alpha) <= probability + 1e-14]
    if not included:
        return 0.0
    return float(binom.cdf(max(included), trials, probability))


def binomial_lower_oracle(successes: int, trials: int, alpha: float) -> float:
    """Independent bisection oracle solving P_p[X >= successes] = alpha."""
    _validate_counts(successes, trials)
    _validate_alpha(alpha)
    if successes == 0:
        return 0.0
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        tail = sum(comb(trials, k) * mid**k * (1-mid)**(trials-k)
                   for k in range(successes, trials + 1))
        if tail < alpha:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def simultaneous_bounds(plans: list[PlanCount], family_alpha: float,
                        method: str) -> list[BoundRow]:
    """Apply a Bonferroni per-plan error budget to a fixed menu."""
    _validate_alpha(family_alpha)
    if method not in ("clopper_pearson", "hoeffding"):
        raise ValueError("method must be clopper_pearson or hoeffding")
    if not plans or len({p.name for p in plans}) != len(plans):
        raise ValueError("a nonempty fixed menu with unique names is required")
    bound = _bound_for(method)
    alpha_each = family_alpha / len(plans)
    return [{"plan": p.name, "cost": p.cost, "successes": p.successes,
             "trials": p.trials, "estimate": p.successes / p.trials,
             "alpha_each": alpha_each,
             "lower": bound(p.successes, p.trials, alpha_each)} for p in plans]


def select_plan(plans: list[PlanCount], target: float, family_alpha: float,
                method: str) -> str:
    """Select cheapest eligible plan; abstain if none certifies the target."""
    if not isfinite(target) or not 0 <= target <= 1:
        raise ValueError("target must be finite and in [0, 1]")
    bounds = simultaneous_bounds(plans, family_alpha, method)
    feasible = [row for row in bounds if row["lower"] >= target]
    if not feasible:
        raise ValueError("no plan certifies the target; abstain")
    return str(min(feasible, key=lambda row: (row["cost"], row["plan"]))["plan"])


def _bound_for(method: str) -> BoundMethod:
    if method == "clopper_pearson":
        return clopper_pearson_lower
    if method == "hoeffding":
        return hoeffding_lower
    raise ValueError("method must be clopper_pearson or hoeffding")
