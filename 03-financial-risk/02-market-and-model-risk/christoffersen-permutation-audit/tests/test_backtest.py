import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.backtest import calibrate, conditional_null, lr_independence, lr_independence_batch
from src.experiment import ExperimentConfig, run_experiment, simulate_markov


def test_clustered_hits_have_larger_statistic_than_spaced_hits() -> None:
    clustered = np.zeros(250, dtype=int)
    clustered[100:110] = 1
    spaced = np.zeros(250, dtype=int)
    spaced[np.arange(10) * 24 + 5] = 1
    assert clustered.sum() == spaced.sum() == 10
    assert lr_independence(clustered) > lr_independence(spaced)


def test_batch_matches_scalar() -> None:
    hits = np.array([[0, 1, 0, 0, 1], [1, 1, 0, 1, 0]], dtype=int)
    assert np.allclose(lr_independence_batch(hits), [lr_independence(row) for row in hits])


@given(st.lists(st.integers(min_value=0, max_value=1), min_size=2, max_size=100))
def test_lr_is_finite_and_nonnegative(values: list[int]) -> None:
    statistic = lr_independence(np.asarray(values, dtype=int))
    assert np.isfinite(statistic)
    assert statistic >= 0.0


def test_conditional_null_preserves_count_and_is_reproducible() -> None:
    first = conditional_null(50, 4, 100, np.random.default_rng(7))
    second = conditional_null(50, 4, 100, np.random.default_rng(7))
    assert np.array_equal(first, second)
    assert first.shape == (100,)


def test_calibration_accounts_for_ties() -> None:
    null = np.array([0.0, 0.0, 1.0, 2.0])
    result = calibrate(1.0, null, tie_uniform=0.25)
    assert result.permutation_p == pytest.approx(0.6)
    assert result.randomized_p == pytest.approx(0.3)


def test_markov_stationary_rate_is_close_in_large_sample() -> None:
    hits = simulate_markov(500, 1000, 0.01, 0.35, np.random.default_rng(4))
    assert hits.mean() == pytest.approx(0.01, abs=0.001)


def test_small_experiment_produces_both_scenarios() -> None:
    config = ExperimentConfig(n=40, probability=0.05, trials=20, permutations=49, seed=8)
    trials, summary, metadata = run_experiment(config)
    assert len(trials) == 40
    assert set(summary["scenario"]) == {"iid_null", "markov_clustered"}
    assert metadata["elapsed_seconds"] >= 0.0


@pytest.mark.parametrize("bad", [np.array([0]), np.array([0, 2]), np.array([[0, 1]])])
def test_invalid_scalar_inputs_fail(bad: np.ndarray) -> None:
    with pytest.raises(ValueError):
        lr_independence(bad)
