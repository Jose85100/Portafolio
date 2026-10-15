import numpy as np
import pytest
from hypothesis import given, strategies as st
from src.oracle import Oracle
from src.posterior import METHODS, posterior, spectral_variances


@pytest.mark.parametrize("method", METHODS)
def test_diagonal_closed_form(method):
    a = np.diag([1.0, 0.1, 0.0])
    y = np.array([0.4, 0.2, 1.0])
    result = posterior(a, y, 0.3, 2.0, method)
    expected = np.array([1.0, 0.1, 0.0]) / (np.array([1.0, 0.1, 0.0]) ** 2 + 0.3**2 / 4) * y
    assert np.allclose(result.mean, expected)
    assert np.allclose(
        np.diag(result.covariance), spectral_variances(np.array([1.0, 0.1, 0.0]), 0.3, 2.0)
    )
    assert result.covariance[2, 2] == pytest.approx(4.0)


@given(st.floats(min_value=0.001, max_value=10), st.floats(min_value=0.001, max_value=10))
def test_prior_variance_bound_and_noise_monotonicity(sigma, tau):
    a = np.diag([1.0, 0.01, 0.0])
    result = posterior(a, np.zeros(3), sigma, tau)
    diagonal = np.diag(result.covariance)
    assert np.all(diagonal >= 0)
    assert np.all(diagonal <= tau * tau * (1 + 1e-12))
    higher = posterior(a, np.zeros(3), min(2 * sigma, 10000), tau)
    assert np.all(np.diag(higher.covariance) + 1e-12 >= diagonal)


@pytest.mark.parametrize("method", METHODS)
def test_tall_matrix_against_independent_oracle(method):
    a = np.array([[1.0, 2.0], [2.0, -0.3], [0.2, 0.1]])
    y = np.array([0.4, 0.2, 0.3])
    actual = posterior(a, y, 0.2, 1.2, method)
    expected = Oracle(a, 0.2, 1.2).evaluate(y)
    assert np.allclose(actual.mean, expected.mean, rtol=1e-12, atol=1e-12)
    assert np.allclose(actual.covariance, expected.covariance, rtol=1e-12, atol=1e-12)


@pytest.mark.parametrize("method", ["svd", "augmented_qr"])
def test_orthogonal_parameter_equivariance(method):
    rng = np.random.default_rng(19)
    a = rng.normal(size=(6, 4))
    y = rng.normal(size=6)
    rotation, _ = np.linalg.qr(rng.normal(size=(4, 4)))
    first = posterior(a, y, 0.1, method=method)
    second = posterior(a @ rotation, y, 0.1, method=method)
    assert np.allclose(first.mean, rotation @ second.mean, atol=1e-12)
    assert np.allclose(first.covariance, rotation @ second.covariance @ rotation.T, atol=1e-12)


@pytest.mark.parametrize(
    "sigma,tau", [(0, 1), (-1, 1), (1, 0), (1, float("nan")), (1e-20, 1), (1, 1e5)]
)
def test_invalid_scales(sigma, tau):
    with pytest.raises(ValueError):
        posterior(np.eye(2), np.zeros(2), sigma, tau)


@pytest.mark.parametrize(
    "a,y",
    [
        (np.ones(3), np.zeros(3)),
        (np.zeros((0, 0)), np.zeros(0)),
        (np.ones((2, 3)), np.zeros(2)),
        (np.eye(2), np.zeros(3)),
        (np.eye(2) * float("nan"), np.zeros(2)),
        (np.eye(2) * 1e5, np.zeros(2)),
        (np.eye(2), np.ones(2) * 1e5),
    ],
)
def test_invalid_inputs(a, y):
    with pytest.raises(ValueError):
        posterior(a, y, 0.1)


def test_unknown_method():
    with pytest.raises(ValueError):
        posterior(np.eye(2), np.zeros(2), 0.1, method="unknown")


def test_zero_operator_keeps_prior():
    result = posterior(np.zeros((3, 2)), np.ones(3), 0.2, tau=2.0)
    assert np.array_equal(result.mean, np.zeros(2))
    assert np.allclose(result.covariance, 4 * np.eye(2))
