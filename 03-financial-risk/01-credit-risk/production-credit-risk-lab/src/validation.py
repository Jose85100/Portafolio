"""Credit-risk validation primitives. Standard library only; no decisions or PII."""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Sequence


def _probabilities(values: Sequence[float]) -> list[float]:
    out = [float(v) for v in values]
    if not out or any(not math.isfinite(v) or not 0 <= v <= 1 for v in out):
        raise ValueError("Expected nonempty finite probabilities in [0, 1]")
    return out


def _labels(values: Sequence[int], n: int) -> list[int]:
    labels = list(values)
    if len(labels) != n or any(v not in (0, 1) for v in labels):
        raise ValueError("Binary labels must match probability vector")
    return labels


def auc_gini(y_true: Sequence[int], pd: Sequence[float]) -> tuple[float, float]:
    """Midrank ROC AUC, correctly handling ties; higher PD indicates more risk."""
    p = _probabilities(pd)
    y = _labels(y_true, len(p))
    n1, n0 = sum(y), len(y) - sum(y)
    if not n1 or not n0:
        raise ValueError("AUC requires both classes")
    ordered = sorted(zip(p, y), key=lambda z: z[0])
    positive_rank_sum = 0.0
    idx = 0
    while idx < len(ordered):
        end = idx + 1
        while end < len(ordered) and ordered[end][0] == ordered[idx][0]:
            end += 1
        average_rank = (idx + 1 + end) / 2
        positive_rank_sum += average_rank * sum(label for _, label in ordered[idx:end])
        idx = end
    auc = (positive_rank_sum - n1 * (n1 + 1) / 2) / (n1 * n0)
    return auc, 2 * auc - 1


def ks_statistic(y_true: Sequence[int], pd: Sequence[float]) -> float:
    """Maximum empirical CDF gap; process equal probability scores as one group."""
    p = _probabilities(pd)
    y = _labels(y_true, len(p))
    positives, negatives = sum(y), len(y) - sum(y)
    if not positives or not negatives:
        raise ValueError("KS requires both classes")
    counts = defaultdict(lambda: [0, 0])
    for score, label in zip(p, y):
        counts[score][label] += 1
    pos_cum = neg_cum = 0
    gap = 0.0
    for score in sorted(counts):
        neg_cum += counts[score][0]
        pos_cum += counts[score][1]
        gap = max(gap, abs(pos_cum / positives - neg_cum / negatives))
    return gap


def brier_score(y_true: Sequence[int], pd: Sequence[float]) -> float:
    p = _probabilities(pd)
    y = _labels(y_true, len(p))
    return sum((label - score) ** 2 for label, score in zip(y, p)) / len(p)


def population_stability_index(reference: Sequence[float], current: Sequence[float],
                               edges: Sequence[float], smoothing: float = 0.5) -> float:
    """PSI using a fixed reference binning contract and additive count smoothing.

    Edges include both endpoints; the final bin includes the right endpoint.
    Avoid reading PSI as a test of model predictive performance.
    """
    ref, cur = _probabilities(reference), _probabilities(current)
    e = [float(z) for z in edges]
    if len(e) < 2 or any(not math.isfinite(x) for x in e) or any(a >= b for a, b in zip(e, e[1:])):
        raise ValueError("Edges must be strictly increasing")
    if e[0] > 0 or e[-1] < 1 or smoothing <= 0 or not math.isfinite(smoothing):
        raise ValueError("Edges must cover [0, 1]; smoothing must be positive")
    def counts(sample):
        result = [smoothing] * (len(e) - 1)
        for v in sample:
            for j in range(len(result)):
                if e[j] <= v < e[j + 1] or (j == len(result) - 1 and v == e[-1]):
                    result[j] += 1
                    break
            else:
                raise ValueError("Value outside edges")
        total = sum(result)
        return [n / total for n in result]
    r, c = counts(ref), counts(cur)
    return sum((a - b) * math.log(a / b) for a, b in zip(c, r))


def ecl_from_conditional_hazards(hazards: Sequence[float], lgd: Sequence[float],
                                 ead: Sequence[float], discount_factors: Sequence[float]) -> float:
    """Sum survival(t-1) * hazard(t) * LGD(t) * EAD(t) * DF(t).

    Conditional hazards are per-period, not cumulative PDs. No post-default cash flows.
    Stage-3 recovery-based ECL is intentionally outside this stage-1/2 kernel.
    """
    h = _probabilities(hazards)
    if not (len(h) == len(lgd) == len(ead) == len(discount_factors)):
        raise ValueError("ECL time vectors must have identical length")
    survival = 1.0
    ecl = 0.0
    for hazard, loss, exposure, df in zip(h, lgd, ead, discount_factors):
        if any(not math.isfinite(float(x)) for x in (loss, exposure, df)):
            raise ValueError("Nonfinite ECL input")
        if not 0 <= loss <= 1 or exposure < 0 or not 0 < df <= 1:
            raise ValueError("Invalid LGD, EAD or discount factor")
        ecl += survival * hazard * loss * exposure * df
        survival *= 1 - hazard
    return ecl


def scenario_weighted_ecl(scenarios: Sequence[tuple[float, float]]) -> float:
    """Tuples of (probability weight, scenario ECL), weights sum to one."""
    if not scenarios:
        raise ValueError("At least one scenario required")
    if any(not math.isfinite(w) or not math.isfinite(e) or w < 0 or e < 0
           for w, e in scenarios):
        raise ValueError("Invalid scenario inputs")
    if not math.isclose(sum(w for w, _ in scenarios), 1.0, rel_tol=0, abs_tol=1e-10):
        raise ValueError("Scenario probabilities must sum to 1")
    return sum(w * e for w, e in scenarios)
