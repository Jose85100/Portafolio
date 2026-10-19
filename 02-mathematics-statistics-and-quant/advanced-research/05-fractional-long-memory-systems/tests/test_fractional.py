import math

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.fractional import apply_filter, budget_memory, coefficient_memory, tail_masses, weights
from src.reference import oracle_filter, prefix_gamma


@pytest.mark.parametrize("d", [0.1, 0.4, 0.8])
def test_oracle_and_prefix(d):
    x = np.random.default_rng(47).normal(size=32)
    w = weights(d, len(x))
    assert np.allclose(apply_filter(x, w), oracle_filter(x, d), atol=1e-13, rtol=1e-13)
    for m in (0, 1, 7, 31):
        assert np.sum(w[: m + 1]) == pytest.approx(prefix_gamma(d, m), abs=1e-13)


@settings(max_examples=70, derandomize=True, deadline=None)
@given(
    d=st.floats(0.02, 0.98),
    xs=st.lists(st.floats(-3, 3, allow_nan=False, allow_infinity=False), min_size=2, max_size=80),
)
def test_tail_error_bound_and_fft(d, xs):
    x = np.asarray(xs, dtype=float)
    w = weights(d, len(x))
    full = apply_filter(x, w)
    m = len(x) // 3
    shortened = apply_filter(x, w, m)
    assert np.max(np.abs(shortened - full)) <= np.max(np.abs(x)) * tail_masses(w)[m] + 1e-12
    assert np.allclose(full, apply_filter(x, w, method="fft"), atol=1e-12, rtol=1e-12)


@settings(max_examples=60, derandomize=True, deadline=None)
@given(d=st.floats(0.02, 0.98), n=st.integers(2, 200), eps=st.floats(0, 1))
def test_minimal_budget_and_signs(d, n, eps):
    w = weights(d, n)
    assert w[0] == 1 and np.all(w[1:] < 0)
    tail = tail_masses(w)
    assert np.all(np.diff(tail) <= 0) and tail[-1] == 0
    m = budget_memory(w, eps)
    assert tail[m] <= eps
    assert m == 0 or tail[m - 1] > eps


def test_constant_attains_tail_bound_and_cutoff_counterexample():
    x = np.ones(8192)
    w = weights(0.4, len(x))
    m = coefficient_memory(w, 0.001)
    assert abs(w[m + 1]) <= 0.001
    error = abs(np.sum(w[: m + 1]) - np.sum(w))
    assert error == pytest.approx(tail_masses(w)[m], abs=1e-12)
    assert error > 20 * 0.001
    assert budget_memory(w, 0.01) > m


def test_impulse_and_zero():
    w = weights(0.4, 16)
    x = np.zeros(16)
    x[0] = 1
    assert np.array_equal(apply_filter(x, w), w)
    assert np.array_equal(apply_filter(np.zeros(16), w), np.zeros(16))
    assert weights(0.4, 1)[0] == 1
    assert budget_memory(weights(0.4, 1), 0) == 0
    assert coefficient_memory(weights(0.4, 1), 0.001) == 0
    assert coefficient_memory(w, 1e-30) == len(w) - 1
    assert coefficient_memory(w, 1) == 0


def test_linear_not_circular_and_no_future_dependency():
    w = weights(0.4, 32)
    x = np.zeros(32)
    x[-1] = 1
    full = apply_filter(x, w)
    fast = apply_filter(x, w, method="fft")
    assert np.all(full[:-1] == 0) and full[-1] == 1
    assert np.max(np.abs(full - fast)) < 1e-12
    circular = np.fft.irfft(np.fft.rfft(x) * np.fft.rfft(w), n=32)
    assert abs(circular[0]) > 0.1


@pytest.mark.parametrize("d", [0, 1, -0.1, math.nan, math.inf])
def test_bad_order(d):
    with pytest.raises(ValueError):
        weights(d, 10)


@pytest.mark.parametrize("n", [0, -1, 1.5, True, 32769])
def test_bad_length(n):
    with pytest.raises(ValueError):
        weights(0.4, n)


@pytest.mark.parametrize(
    "w", [np.array([]), np.ones((2, 2)), np.array([1, math.nan]), np.array([2, -0.1]), np.array([1, 0.1])]
)
def test_bad_weights(w):
    with pytest.raises(ValueError):
        tail_masses(w)


@pytest.mark.parametrize("eps", [-1, math.nan, math.inf])
def test_bad_budget(eps):
    with pytest.raises(ValueError):
        budget_memory(weights(0.4, 8), eps)


@pytest.mark.parametrize("eps", [0, -1, math.nan])
def test_bad_coefficient_epsilon(eps):
    with pytest.raises(ValueError):
        coefficient_memory(weights(0.4, 8), eps)


@pytest.mark.parametrize("x", [np.array([]), np.ones((2, 2)), np.array([math.nan]), np.array([1e100])])
def test_bad_series(x):
    with pytest.raises(ValueError):
        apply_filter(x, np.ones(1))


def test_bad_filter_options_and_oracle_domain():
    with pytest.raises(ValueError):
        apply_filter(np.ones(8), weights(0.4, 7))
    for m in (-1, 8, True, 1.5):
        with pytest.raises(ValueError):
            apply_filter(np.ones(8), weights(0.4, 8), m)
    with pytest.raises(ValueError):
        apply_filter(np.ones(8), weights(0.4, 8), method="circular")
    for x in (np.ones(257), np.array([]), np.array([math.inf]), np.ones((2, 2))):
        with pytest.raises(ValueError):
            oracle_filter(x, 0.4)
