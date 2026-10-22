"""Auditable binary consensus under shared agent errors.

No LLM is executed: agents are simulated Bernoulli voters. Provenance groups are
metadata known before labels; training truth is used only for reliability weights.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log
from random import Random
from typing import Sequence


@dataclass(frozen=True)
class Case:
    case_id: int
    truth: int
    votes: tuple[int, ...]


@dataclass(frozen=True)
class Decision:
    prediction: int
    confidence: float  # absolute normalized voting margin, NOT a calibrated probability


REGIMES = {
    "shared_failure": 0.20,
    "mild_dependence": 0.07,
    "independent": 0.00,
}
PROVENANCE = ("provider_A", "provider_A", "provider_A", "provider_B", "provider_C")
POLICIES = ("majority", "weighted", "group_capped", "wrong_metadata")


def generate_cases(seed: int, n: int, shared_failure: float) -> list[Case]:
    """Generate independent cases, with 3 votes sharing a latent failure event."""
    if n <= 0 or not 0 <= shared_failure <= 1:
        raise ValueError("n must be positive and shared_failure within [0, 1]")
    rng = Random(seed)
    cases: list[Case] = []
    for case_id in range(n):
        truth = rng.randrange(2)
        shock = rng.random() < shared_failure
        votes = []
        for i in range(5):
            correct = (not shock and rng.random() < 0.92) if i < 3 else rng.random() < 0.82
            votes.append(truth if correct else 1 - truth)
        cases.append(Case(case_id, truth, tuple(votes)))
    return cases


def fit_reliabilities(calibration: Sequence[Case]) -> tuple[float, ...]:
    """Laplace-smoothed per-agent log odds, using calibration labels only."""
    if not calibration:
        raise ValueError("empty calibration")
    if any(len(c.votes) != 5 or c.truth not in (0, 1) or any(v not in (0, 1) for v in c.votes) for c in calibration):
        raise ValueError("invalid case")
    n = len(calibration)
    weights = []
    for i in range(5):
        correct = sum(c.votes[i] == c.truth for c in calibration)
        p = min(0.99, max(0.51, (correct + 1) / (n + 2)))
        weights.append(log(p / (1 - p)))
    return tuple(weights)


def decide(votes: Sequence[int], weights: Sequence[float], policy: str,
           groups: Sequence[str] = PROVENANCE) -> Decision:
    """Return binary prediction and voting margin; deterministic ties choose 0."""
    if len(votes) != 5 or len(weights) != 5 or len(groups) != 5:
        raise ValueError("five agents and five group labels are required")
    if any(v not in (0, 1) for v in votes):
        raise ValueError("votes must be binary")
    if any(not isfinite(w) or w <= 0 for w in weights):
        raise ValueError("weights must be finite and positive")
    if policy not in POLICIES:
        raise ValueError("unknown policy")
    signed = [2 * v - 1 for v in votes]
    if policy == "majority":
        numerator = float(sum(signed))
        denominator = 5.0
    elif policy == "weighted":
        numerator = sum(w * s for w, s in zip(weights, signed))
        denominator = sum(weights)
    else:
        if policy == "wrong_metadata":
            groups = ("unknown",) * 5
        # A provenance group contributes ONE normalized vote, regardless of size.
        # This is an engineering heuristic, not an optimal correlated-error model.
        group_values: dict[str, list[tuple[float, int]]] = {}
        for group, weight, sign in zip(groups, weights, signed):
            group_values.setdefault(group, []).append((weight, sign))
        numerator = 0.0
        denominator = 0.0
        for members in group_values.values():
            total = sum(w for w, _ in members)
            numerator += sum(w * sign for w, sign in members) / total
            denominator += 1.0
    confidence = min(1.0, abs(numerator) / denominator)
    return Decision(int(numerator > 0), confidence)


def evaluate(cases: Sequence[Case], weights: Sequence[float], policy: str,
             coverage: float = 0.8) -> dict[str, float]:
    """Accuracy and error on the top confidence fraction (exact finite-sample coverage)."""
    if not cases or not 0 < coverage <= 1:
        raise ValueError("nonempty cases and coverage in (0,1] required")
    if policy not in POLICIES:
        raise ValueError("unknown policy")
    decisions = [decide(c.votes, weights, policy) for c in cases]
    correct = [int(d.prediction == c.truth) for d, c in zip(decisions, cases)]
    selected = sorted(range(len(cases)), key=lambda i: (-decisions[i].confidence, cases[i].case_id))
    k = max(1, int(len(cases) * coverage))
    errors = sum(1 - correct[i] for i in selected[:k])
    # Discrete AURC: risk of each prefix of confidence-ranked predictions.
    cumulative_errors = 0
    aurc = 0.0
    for j, i in enumerate(selected, start=1):
        cumulative_errors += 1 - correct[i]
        aurc += cumulative_errors / j
    return {
        "accuracy": sum(correct) / len(cases),
        "risk_at_80": errors / k,
        "coverage": k / len(cases),
        "aurc": aurc / len(cases),
        "mean_margin": sum(d.confidence for d in decisions) / len(decisions),
    }
