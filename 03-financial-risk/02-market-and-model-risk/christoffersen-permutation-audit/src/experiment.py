"""Reproducible finite-sample size and power experiment."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from .backtest import calibrate, conditional_null, lr_independence_batch


@dataclass(frozen=True)
class ExperimentConfig:
    n: int = 250
    probability: float = 0.01
    trials: int = 2_000
    permutations: int = 1_999
    cluster_probability: float = 0.35
    alpha: float = 0.05
    seed: int = 20261021


def simulate_markov(
    trials: int, n: int, stationary_probability: float, p11: float, rng: np.random.Generator
) -> NDArray[np.int8]:
    """Simulate a stationary two-state chain with a specified hit probability."""
    if not 0 < stationary_probability < 1 or not 0 <= p11 < 1:
        raise ValueError("invalid Markov probabilities")
    p01 = stationary_probability * (1.0 - p11) / (1.0 - stationary_probability)
    if p01 > 1:
        raise ValueError("infeasible transition probabilities")
    hits = np.zeros((trials, n), dtype=np.int8)
    hits[:, 0] = rng.binomial(1, stationary_probability, size=trials)
    draws = rng.random((trials, n - 1))
    for t in range(1, n):
        probability = np.where(hits[:, t - 1] == 1, p11, p01)
        hits[:, t] = draws[:, t - 1] < probability
    return hits


def _evaluate(
    hits: NDArray[np.int8], config: ExperimentConfig, rng: np.random.Generator
) -> tuple[pd.DataFrame, int]:
    statistics = lr_independence_batch(hits)
    counts = hits.sum(axis=1)
    cache: dict[int, NDArray[np.float64]] = {}
    rows: list[dict[str, float | int | bool]] = []
    for index, (statistic, count) in enumerate(zip(statistics, counts, strict=True)):
        k = int(count)
        if k not in cache:
            cache[k] = conditional_null(config.n, k, config.permutations, rng)
        result = calibrate(float(statistic), cache[k], float(rng.random()))
        rows.append(
            {
                "trial": index,
                "exceptions": k,
                "lr_ind": result.statistic,
                "p_asymptotic": result.asymptotic_p,
                "p_permutation": result.permutation_p,
                "p_randomized": result.randomized_p,
                "reject_asymptotic": result.asymptotic_p < config.alpha,
                "reject_permutation": result.permutation_p < config.alpha,
                "reject_randomized": result.randomized_p < config.alpha,
            }
        )
    return pd.DataFrame(rows), len(cache)


def run_experiment(config: ExperimentConfig) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float | int]]:
    """Measure empirical size under iid hits and power under clustered stationary hits."""
    rng = np.random.default_rng(config.seed)
    started = perf_counter()
    iid = rng.binomial(1, config.probability, size=(config.trials, config.n)).astype(np.int8)
    clustered = simulate_markov(config.trials, config.n, config.probability, config.cluster_probability, rng)
    iid_trials, iid_cache = _evaluate(iid, config, rng)
    clustered_trials, clustered_cache = _evaluate(clustered, config, rng)
    iid_trials.insert(0, "scenario", "iid_null")
    clustered_trials.insert(0, "scenario", "markov_clustered")
    trials = pd.concat([iid_trials, clustered_trials], ignore_index=True)
    summary_rows = []
    for scenario, frame in trials.groupby("scenario", sort=False):
        summary_rows.append(
            {
                "scenario": scenario,
                "mean_exception_rate": frame["exceptions"].mean() / config.n,
                "rejection_asymptotic": frame["reject_asymptotic"].mean(),
                "rejection_permutation": frame["reject_permutation"].mean(),
                "rejection_randomized": frame["reject_randomized"].mean(),
            }
        )
    summary = pd.DataFrame(summary_rows)
    metadata: dict[str, float | int] = {
        "elapsed_seconds": perf_counter() - started,
        "iid_cached_exception_counts": iid_cache,
        "clustered_cached_exception_counts": clustered_cache,
    }
    return trials, summary, metadata
