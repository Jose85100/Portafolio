"""Off-policy evaluation with deterministic, cross-fitted categorical rewards.

All estimators are for a two-action contextual bandit with observed binary X.
A target action is deterministic: action 1 when X=0, else action 0.
No production/causal identification claims are made beyond the synthetic DGP.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Literal

REWARDS: tuple[tuple[float, float], tuple[float, float]] = (
    (0.15, 0.55), (0.70, 0.30)
)
METHODS = ("ips", "snips", "dm", "dr", "clipped_ips", "clipped_dr")


def target_action(context: int) -> int:
    if context not in (0, 1):
        raise ValueError("context must be 0 or 1")
    return 1 - context


def true_value() -> float:
    """Exact value under P(X=0)=P(X=1)=1/2."""
    return 0.5 * (REWARDS[0][1] + REWARDS[1][0])


@dataclass(frozen=True)
class Log:
    contexts: tuple[int, ...]
    actions: tuple[int, ...]
    rewards: tuple[int, ...]
    reported_propensities: tuple[float, ...]
    actual_target_probability: float

    def validate(self) -> None:
        n = len(self.contexts)
        if n < 4 or any(len(v) != n for v in (
            self.actions, self.rewards, self.reported_propensities
        )):
            raise ValueError("all vectors must have the same length >=4")
        for x, a, r, p in zip(
            self.contexts, self.actions, self.rewards, self.reported_propensities
        ):
            if x not in (0, 1) or a not in (0, 1) or r not in (0, 1):
                raise ValueError("invalid binary context/action/reward")
            if not math.isfinite(p) or not (0 < p <= 1):
                raise ValueError("invalid reported propensity: positivity required")
        if not (0 < self.actual_target_probability <= 1):
            raise ValueError("actual behavior lacks target-policy support")


def simulate(
    seed: int,
    n: int = 600,
    target_probability: float = 0.5,
    reported_probability: float | None = None,
) -> Log:
    if n < 4:
        raise ValueError("n must be >=4")
    if not (0 < target_probability <= 1):
        raise ValueError("behavior must have positive target support")
    if reported_probability is None:
        reported_probability = target_probability
    if not (0 < reported_probability <= 1):
        raise ValueError("reported probability must be positive")
    rng = random.Random(seed)
    contexts: list[int] = []
    actions: list[int] = []
    rewards: list[int] = []
    props: list[float] = []
    for _ in range(n):
        x = int(rng.random() >= 0.5)
        a = target_action(x) if rng.random() < target_probability else x
        p = reported_probability if a == target_action(x) else 1 - reported_probability
        r = int(rng.random() < REWARDS[x][a])
        contexts.append(x)
        actions.append(a)
        rewards.append(r)
        props.append(p)
    log = Log(tuple(contexts), tuple(actions), tuple(rewards), tuple(props), target_probability)
    log.validate()
    return log


def crossfit_reward(log: Log, folds: int = 3, prior_strength: float = 2.0) -> tuple[float, ...]:
    """Out-of-fold E[R | X, target(X)]; no row trains its own prediction.

    A smoothed cell mean (Beta(1,1) when prior_strength=2) is deliberately
    low-dimensional. Fold membership is i % folds and independent of outcomes.
    """
    log.validate()
    if not 2 <= folds <= len(log.contexts):
        raise ValueError("invalid folds")
    if prior_strength <= 0 or not math.isfinite(prior_strength):
        raise ValueError("prior_strength must be finite and positive")
    totals = [[0, 0] for _ in range(2)]  # [count, reward sum] by X, target action only
    per_fold = [[[0, 0] for _ in range(2)] for _ in range(folds)]
    for i, (x, a, r) in enumerate(zip(log.contexts, log.actions, log.rewards)):
        if a == target_action(x):
            totals[x][0] += 1
            totals[x][1] += r
            per_fold[i % folds][x][0] += 1
            per_fold[i % folds][x][1] += r
    predictions: list[float] = []
    for i, x in enumerate(log.contexts):
        count = totals[x][0] - per_fold[i % folds][x][0]
        reward_sum = totals[x][1] - per_fold[i % folds][x][1]
        predictions.append((reward_sum + 0.5 * prior_strength) / (count + prior_strength))
    return tuple(predictions)


def _mean(values: list[float]) -> float:
    return math.fsum(values) / len(values)


@dataclass(frozen=True)
class Estimate:
    method: str
    value: float
    ess: float
    max_weight: float
    matched: int
    warning: str


def estimate(
    log: Log,
    method: Literal["ips", "snips", "dm", "dr", "clipped_ips", "clipped_dr"],
    *,
    clip: float = 8.0,
    min_ess: float = 30.0,
    predictions: tuple[float, ...] | None = None,
) -> Estimate:
    log.validate()
    if method not in METHODS:
        raise ValueError("unknown estimator")
    if clip <= 0 or not math.isfinite(clip) or min_ess < 0:
        raise ValueError("invalid clipping or ESS threshold")
    if predictions is None:
        predictions = crossfit_reward(log)
    if len(predictions) != len(log.contexts) or any(
        not math.isfinite(v) or not 0 <= v <= 1 for v in predictions
    ):
        raise ValueError("invalid out-of-fold predictions")
    weights = [
        1.0 / p if a == target_action(x) else 0.0
        for x, a, p in zip(log.contexts, log.actions, log.reported_propensities)
    ]
    weight_sum = math.fsum(weights)
    weight_square_sum = math.fsum(w * w for w in weights)
    ess = weight_sum * weight_sum / weight_square_sum if weight_square_sum else 0.0
    matched = sum(w > 0 for w in weights)
    warning = "LOW_ESS" if ess < min_ess else "OK"
    if matched == 0:
        warning = "NO_OBSERVED_TARGET_ACTION"
    if method == "snips":
        value = (
            math.fsum(w * r for w, r in zip(weights, log.rewards)) / weight_sum
            if weight_sum else float("nan")
        )
    else:
        terms: list[float] = []
        for w, r, mu in zip(weights, log.rewards, predictions):
            if method == "ips":
                terms.append(w * r)
            elif method == "clipped_ips":
                terms.append(min(w, clip) * r)
            elif method == "dm":
                terms.append(mu)
            elif method == "dr":
                terms.append(mu + w * (r - mu))
            else:
                terms.append(mu + min(w, clip) * (r - mu))
        value = _mean(terms)
    return Estimate(method, value, ess, max(weights), matched, warning)
