import numpy as np
import pytest
from hypothesis import given, settings, strategies as st
from src.kl_robust import kl, mean_variance_approximation, robust_expectation, validate
from src.reference import bernoulli_oracle, slsqp_reference


@pytest.mark.parametrize("probability", [0.001, 0.1, 0.7])
@pytest.mark.parametrize("radius", [0.0, 0.001, 0.01, 0.1, 1.0, 10.0])
def test_binary_independent_oracle(probability, radius):
    p = np.array([1 - probability, probability])
    loss = np.array([0.0, 1.0])
    result = robust_expectation(p, loss, radius)
    assert result.value == pytest.approx(bernoulli_oracle(probability, radius), abs=1e-10)
    assert result.divergence <= radius + 1e-10
    assert abs(result.q.sum() - 1) < 1e-12
    assert result.upper >= result.value - 1e-12
    assert result.upper - result.value < 1e-9


@given(
    st.floats(min_value=0.0001, max_value=1),
    st.floats(min_value=0.1, max_value=10),
    st.floats(min_value=-100, max_value=100),
)
@settings(derandomize=True, max_examples=40)
def test_monotonicity_and_positive_affine_equivariance(radius, scale, offset):
    p = np.array([0.2, 0.3, 0.5])
    loss = np.array([-1.0, 0.0, 2.0])
    first = robust_expectation(p, loss, radius)
    second = robust_expectation(p, loss, 2 * radius)
    changed = robust_expectation(p, scale * loss + offset, radius)
    assert second.value >= first.value - 1e-10
    assert np.allclose(first.q, changed.q, atol=1e-9)
    assert changed.value == pytest.approx(scale * first.value + offset, abs=1e-8)


def test_constant_and_single_atom():
    result = robust_expectation(np.array([0.3, 0.7]), np.array([2.0, 2.0]), 0.4)
    assert result.regime == "constant" and result.value == pytest.approx(2.0)
    assert robust_expectation(np.ones(1), np.array([-3.0]), 1).value == -3.0


def test_saturation_with_tied_maximum():
    p = np.array([0.1, 0.2, 0.7])
    loss = np.array([2.0, 2.0, 0.0])
    result = robust_expectation(p, loss, 2.0)
    assert result.regime == "saturated"
    assert np.allclose(result.q, [1 / 3, 2 / 3, 0])
    assert result.value == 2.0


def test_approximation_is_not_an_upper_bound():
    p = np.array([0.999, 0.001])
    loss = np.array([0.0, 1.0])
    assert (
        mean_variance_approximation(p, loss, 0.01) < robust_expectation(p, loss, 0.01).value - 0.001
    )
    assert mean_variance_approximation(np.array([0.5, 0.5]), loss, 10) > 1


@pytest.mark.parametrize("variant", ["initial", "two_start", "refined"])
def test_slsqp_competitive_baseline(variant):
    p = np.array([0.2, 0.3, 0.5])
    loss = np.array([0.1, 0.8, 0.3])
    first = robust_expectation(p, loss, 0.05)
    second = slsqp_reference(p, loss, 0.05, variant=variant)
    assert second.success
    assert second.divergence <= 0.05 + 1e-8
    assert abs(first.value - second.value) < 1e-6


def test_invalid_slsqp_variant():
    with pytest.raises(ValueError):
        slsqp_reference(np.ones(1), np.zeros(1), 0.1, variant="unknown")


@pytest.mark.parametrize(
    "p,loss,radius",
    [
        (np.array([]), np.array([]), 0.1),
        (np.array([0.5, 0.5]), np.ones(3), 0.1),
        (np.array([0.4, 0.5]), np.ones(2), 0.1),
        (np.array([0.0, 1.0]), np.ones(2), 0.1),
        (np.array([-1.0, 2.0]), np.ones(2), 0.1),
        (np.array([1.0]), np.array([float("nan")]), 0.1),
        (np.ones(1), np.ones(1), -1),
        (np.ones(1), np.ones(1), float("inf")),
        (np.ones(1), np.array([1e7]), 0.1),
        (np.ones(1), np.ones(1), 101),
    ],
)
def test_invalid_inputs(p, loss, radius):
    with pytest.raises(ValueError):
        validate(p, loss, radius)


def test_zero_q_kl_convention():
    assert kl(np.array([1.0, 0.0]), np.array([0.5, 0.5])) == pytest.approx(np.log(2))


def test_tiny_positive_radius_explicitly_refused():
    with pytest.raises(ValueError):
        robust_expectation(np.array([0.5, 0.5]), np.array([0.0, 1.0]), 1e-14)


@pytest.mark.parametrize("probability,radius", [(0, 0.1), (1, 0.1), (0.5, -1), (0.5, float("nan"))])
def test_invalid_binary_inputs(probability, radius):
    with pytest.raises(ValueError):
        bernoulli_oracle(probability, radius)
