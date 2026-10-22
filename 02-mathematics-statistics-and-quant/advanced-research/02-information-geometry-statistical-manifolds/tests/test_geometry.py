import math
import numpy as np
import pytest
from hypothesis import given, strategies as st
from scipy.stats import chi2_contingency
from src.geometry import fisher_rao, hellinger, local_fisher, geodesic, simplex
from src.reference import oracle_fr
from src.testing import permutation_test, counts_pair, monte_carlo_p


@pytest.mark.parametrize("p", [[-1, 2], [0.1, 0.2], [np.nan, 1], [np.inf, 0], [[0.5, 0.5]], [1]])
def test_invalid_simplex(p):
    with pytest.raises(ValueError):
        simplex(np.array(p))


def test_invalid_pair():
    with pytest.raises(ValueError):
        fisher_rao(np.array([0.5, 0.5]), np.ones(3) / 3)


def test_boundaries():
    a = np.array([1.0, 0])
    b = a[::-1]
    assert fisher_rao(a, b) == pytest.approx(math.pi)
    assert hellinger(a, b) == pytest.approx(1)
    assert fisher_rao(a, a) == 0
    with pytest.raises(ValueError):
        local_fisher(a, b)


@given(st.lists(st.floats(min_value=0.001, max_value=1, allow_nan=False), min_size=6, max_size=6))
def test_metric_properties(values):
    a = np.array(values[:2])
    a /= a.sum()
    b = np.array(values[2:4])
    b /= b.sum()
    c = np.array(values[4:])
    c /= c.sum()
    d = fisher_rao(a, b)
    assert d == pytest.approx(fisher_rao(b, a), abs=1e-14)
    assert 0 <= d <= math.pi
    assert d <= fisher_rao(a, c) + fisher_rao(c, b) + 1e-12
    assert d == pytest.approx(4 * np.arcsin(hellinger(a, b) / math.sqrt(2)), abs=1e-14)
    for t in [0, 0.2, 0.5, 1]:
        g = geodesic(a, b, t)
        assert g.sum() == pytest.approx(1)
        assert np.all(g >= 0)
        assert fisher_rao(a, g) == pytest.approx(t * d, abs=1e-11)


@pytest.mark.parametrize("t", [-0.1, 1.1, np.nan])
def test_bad_geodesic(t):
    with pytest.raises(ValueError):
        geodesic(np.array([0.5, 0.5]), np.array([0.9, 0.1]), t)


def test_equal_geodesic():
    a = np.array([0.25, 0.75])
    np.testing.assert_allclose(geodesic(a, a, 0.5), a)


def test_oracle():
    for eps in [0, 1e-12, 0.01, 0.3]:
        a = np.array([0.5, 0.5])
        b = np.array([0.5 + eps, 0.5 - eps])
        assert fisher_rao(a, b) == pytest.approx(oracle_fr(a, b), abs=1e-14)


def test_local_not_global():
    a = np.array([0.99, 0.01])
    b = np.array([0.5, 0.5])
    assert local_fisher(a, b) > math.pi
    assert local_fisher(a, b) > 4 * local_fisher(b, a)


@pytest.mark.parametrize(
    "a,b",
    [
        ([1.5, 2], [1, 2]),
        ([-1, 3], [1, 2]),
        ([np.nan, 1], [1, 2]),
        ([0, 0], [1, 2]),
        ([1], [1]),
        ([1, 2], [1, 2, 3]),
        ([100001, 0], [1, 2]),
    ],
)
def test_invalid_counts(a, b):
    with pytest.raises(ValueError):
        counts_pair(np.array(a), np.array(b))


@pytest.mark.parametrize("permutations", [0, 10001, True, 1.2])
def test_invalid_permutations(permutations):
    with pytest.raises(ValueError):
        permutation_test(np.array([1, 2]), np.array([2, 1]), permutations, 1)


@pytest.mark.parametrize("obs,null", [(np.nan, [1]), (1, []), (1, [np.nan]), (1, [[1]])])
def test_invalid_mc(obs, null):
    with pytest.raises(ValueError):
        monte_carlo_p(obs, np.array(null))


def test_no_zero_pvalue():
    assert monte_carlo_p(10, np.arange(9)) == pytest.approx(0.1)


def test_exact_ties():
    assert monte_carlo_p(1, np.ones(9)) == 1


def test_permutations_reproducible():
    a = np.array([90, 5, 4, 1])
    b = np.array([50, 20, 20, 10])
    r = permutation_test(a, b, 99, 42)
    assert r == permutation_test(a, b, 99, 42)
    assert r["p_fr"] == r["p_hellinger"]
    assert r["p_fr"] >= 0.01


def test_pearson_reference():
    a = np.array([20.0, 30, 50])
    b = np.array([40.0, 50, 10])
    r = permutation_test(a, b, 9, 1)
    scipy = chi2_contingency(np.stack([a, b]), correction=False)
    assert r["pearson"] == pytest.approx(scipy.statistic)
    assert r["p_pearson_asymptotic"] == pytest.approx(scipy.pvalue)


def test_single_active_category():
    r = permutation_test(np.array([4, 0]), np.array([3, 0]), 9, 1)
    assert r["p_fr"] == r["p_pearson_asymptotic"] == 1


def test_unequal_samples():
    r = permutation_test(np.array([3, 7]), np.array([10, 30]), 19, 2)
    assert r["p_fr"] == r["p_hellinger"]
