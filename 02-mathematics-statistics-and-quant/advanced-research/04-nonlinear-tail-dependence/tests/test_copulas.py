import math

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from scipy.stats import kendalltau, norm

from src.copulas import (
    Copula,
    asymptotic_lambda,
    conditional,
    conditional_exceedance,
    conditional_values,
    direct,
    kendall_tau,
    sample_latent,
    threshold,
)
from src.reference import conditional_second_moment, latent_coordinate_reference, tail_coordinate_reference


@pytest.mark.parametrize("df", [None, 4, 30])
def test_variance_bound(df):
    model = Copula(0.5, df)
    q = 0.99
    lam, _ = tail_coordinate_reference(model, q)
    second = conditional_second_moment(model, q)
    assert second <= lam + 1e-12
    ratio = (second - lam * lam) / (lam / (1 - q) - lam * lam)
    bound = (1 - q) * (1 - lam) / (1 - (1 - q) * lam)
    assert ratio <= bound + 1e-12


@pytest.mark.parametrize("rho,df", [(1, None), (-1, 4), (math.nan, 4), (0, 0), (0, math.inf), (0, 101)])
def test_invalid_model(rho, df):
    with pytest.raises(ValueError):
        Copula(rho, df)


@pytest.mark.parametrize("q", [0.4, 1, math.nan, math.inf])
def test_invalid_q(q):
    with pytest.raises(ValueError):
        threshold(Copula(0.5), q)


@pytest.mark.parametrize("n", [0, 1, 2.5, True, 10000001])
def test_invalid_n(n):
    with pytest.raises(ValueError):
        sample_latent(Copula(0.5), n, np.random.default_rng(1))


@settings(max_examples=40, derandomize=True, deadline=None)
@given(rho=st.floats(-0.9, 0.9), df=st.floats(2.1, 80))
def test_matching_tau_and_positive_t_tail(rho, df):
    assert kendall_tau(Copula(rho)) == kendall_tau(Copula(rho, df))
    assert asymptotic_lambda(Copula(rho)) == 0
    assert 0 < asymptotic_lambda(Copula(rho, df)) < 1


@settings(max_examples=30, derandomize=True, deadline=None)
@given(q=st.floats(0.5, 0.9999))
def test_independence_population(q):
    model = Copula(0)
    values = conditional_values(model, q, np.array([0.0, 0.4, 0.999999]))
    assert np.allclose(values, 1 - q, atol=1e-13)


@pytest.mark.parametrize("df", [None, 4, 30])
def test_quadrature_coordinates(df):
    model = Copula(0.5, df)
    a, _ = tail_coordinate_reference(model, 0.999)
    b, _ = latent_coordinate_reference(model, 0.999)
    assert a == pytest.approx(b, abs=2e-8)


def test_gaussian_independence_reference():
    for q in (0.9, 0.99, 0.9999):
        assert tail_coordinate_reference(Copula(0), q)[0] == pytest.approx(1 - q, abs=1e-12)


def test_zero_rho_t_is_not_independent():
    model = Copula(0, 4)
    assert kendall_tau(model) == 0
    assert asymptotic_lambda(model) > 0.05
    assert tail_coordinate_reference(model, 0.999)[0] > 0.05


def test_conditional_normal_formula():
    x = np.array([-1.0, 0.0, 2.0])
    assert np.allclose(conditional_exceedance(Copula(0.5), x, 1), norm.sf((1 - 0.5 * x) / math.sqrt(0.75)))


@pytest.mark.parametrize(
    "u", [np.array([1.0]), np.array([-0.1]), np.array([math.nan]), np.ones((2, 2)), np.array([])]
)
def test_uniform_endpoints(u):
    with pytest.raises(ValueError):
        conditional_values(Copula(0.5), 0.99, u)


@pytest.mark.parametrize(
    "x,a", [(np.array([math.nan]), 1), (np.array([0.0]), math.inf), (np.array([1e200]), 1)]
)
def test_bad_conditioning(x, a):
    with pytest.raises(ValueError):
        conditional_exceedance(Copula(0.5), x, a)


def test_seed_margins_and_rank():
    model = Copula(0.5, 4)
    a = sample_latent(model, 10000, np.random.default_rng(82))
    b = sample_latent(model, 10000, np.random.default_rng(82))
    assert np.array_equal(a, b)
    assert abs(kendalltau(a[:, 0], a[:, 1]).statistic - kendall_tau(model)) < 0.03
    assert abs(np.mean(a[:, 0] > threshold(model, 0.99)) - 0.01) < 0.004


def test_direct_zero_denominator_is_not_silently_zero():
    r = direct(Copula(0), 0.99999, 2, np.random.default_rng(3))
    assert r["estimate"] == 0
    assert r["marginal_count"] == 0
    assert r["random_denominator_estimate"] is None


def test_conditional_estimator_and_gaussian_seed():
    r = conditional(Copula(0), 0.99, 20, np.random.default_rng(2))
    assert r["estimate"] == pytest.approx(0.01)
    assert r["sample_se"] < 1e-15
    z = sample_latent(Copula(0), 10, np.random.default_rng(1))
    assert z.shape == (10, 2)


def test_finite_threshold_is_not_asymptotic_limit():
    model = Copula(0.5, 4)
    finite = tail_coordinate_reference(model, 0.99)[0]
    assert finite - asymptotic_lambda(model) > 0.01
    assert tail_coordinate_reference(Copula(0.5), 0.99)[0] > 0.1
