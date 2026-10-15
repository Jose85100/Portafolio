import numpy as np
import pytest
from hypothesis import given, settings, strategies as st
from src.reference import linear_program, monotone_w2_squared
from src.transport import residual, round_plan, sinkhorn, validate


@pytest.mark.parametrize("method", ["naive", "log"])
def test_exact_two_atom_counterexample(method):
    a, b = np.array([0.9, 0.1]), np.array([0.1, 0.9])
    c = np.array([[0.0, 1.0], [1.0, 0.0]])
    result = sinkhorn(a, b, c, 0.01, method, max_iterations=1)
    assert result.raw_cost < 1e-20
    assert result.raw_residual == pytest.approx(1.6)
    assert not result.converged
    assert result.upper == pytest.approx(0.8)
    assert result.rounded_residual < 1e-12
    assert result.lower <= 0.8 + 1e-12


def test_underflow_explicit_not_silent():
    a = np.array([0.5, 0.5])
    c = np.array([[400.0, 441.0], [361.0, 400.0]])
    with pytest.raises(FloatingPointError):
        sinkhorn(a, a, c, 0.005, "naive")
    result = sinkhorn(a, a, c, 0.005, "log", max_iterations=50)
    assert np.isfinite(result.plan).all()
    assert result.rounded_residual < 1e-12


@given(st.lists(st.floats(min_value=0.01, max_value=2, allow_nan=False), min_size=6, max_size=6))
@settings(derandomize=True, max_examples=50)
def test_rounding_nonnegativity_and_marginals(values):
    p = np.array(values).reshape(2, 3)
    a = np.array([0.7, 0.3])
    b = np.array([0.1, 0.2, 0.7])
    result = round_plan(p, a, b)
    assert result.min() >= 0
    assert residual(result, a, b) < 1e-12
    assert np.allclose(round_plan(result, a, b), result, atol=1e-12)


@pytest.mark.parametrize("epsilon", [1.0, 0.1, 0.01])
def test_independent_lp_quantiles_and_bounds(epsilon):
    x = np.array([0.0, 0.3, 1.0])
    y = np.array([0.1, 0.8])
    a = np.array([0.2, 0.5, 0.3])
    b = np.array([0.6, 0.4])
    c = (x[:, None] - y[None, :]) ** 2
    truth, plan = linear_program(a, b, c)
    assert truth == pytest.approx(monotone_w2_squared(x, y, a, b), abs=1e-12)
    assert residual(plan, a, b) < 1e-9
    result = sinkhorn(a, b, c, epsilon)
    assert result.lower <= truth + 1e-10 <= result.upper + 1e-10


def test_zeros_and_single_atom():
    a = np.array([0.0, 1.0])
    b = np.array([1.0])
    c = np.array([[0.0], [3.0]])
    result = sinkhorn(a, b, c, 0.1)
    assert result.upper == pytest.approx(3.0)
    assert np.array_equal(result.plan, np.array([[0.0], [1.0]]))
    assert monotone_w2_squared(np.array([5.0, 0.0]), np.array([2.0]), a, b) == pytest.approx(4.0)


def test_zero_plan_repaired_to_independent_coupling():
    a = np.array([0.2, 0.8])
    b = np.array([0.6, 0.4])
    assert np.allclose(round_plan(np.zeros((2, 2)), a, b), np.outer(a, b))


def test_regularized_transport_cost_is_not_exact_wasserstein():
    a = np.array([0.5, 0.5])
    c = np.array([[0.0, 1.0], [1.0, 0.0]])
    result = sinkhorn(a, a, c, 1.0)
    assert result.upper == pytest.approx(1 / (1 + np.exp(1.0)))
    truth, _ = linear_program(a, a, c)
    assert truth == 0


def test_cost_offset_equivariance():
    a = np.array([0.4, 0.6])
    b = np.array([0.7, 0.3])
    c = np.array([[0.0, 1.0], [1.0, 0.0]])
    first = sinkhorn(a, b, c, 0.2)
    second = sinkhorn(a, b, c + 400, 0.2)
    assert np.allclose(first.plan, second.plan, atol=1e-10)
    assert second.upper - first.upper == pytest.approx(400.0)


@pytest.mark.parametrize(
    "a,b,c",
    [
        (np.array([]), np.array([1.0]), np.zeros((0, 1))),
        (np.array([0.5]), np.array([1.0]), np.zeros((1, 1))),
        (np.array([-1.0, 2.0]), np.array([1.0]), np.zeros((2, 1))),
        (np.array([1.0]), np.array([1.0]), np.ones((2, 1))),
        (np.array([1.0]), np.array([1.0]), np.array([[float("nan")]])),
        (np.array([1.0]), np.array([1.0]), np.array([[-1.0]])),
        (np.array([1.0]), np.array([1.0]), np.array([[1e7]])),
    ],
)
def test_invalid_masses_and_costs(a, b, c):
    with pytest.raises(ValueError):
        validate(a, b, c)


@pytest.mark.parametrize(
    "options",
    [
        {"epsilon": 0},
        {"epsilon": float("nan")},
        {"epsilon": 1e-10},
        {"epsilon": 0.1, "max_iterations": True},
        {"epsilon": 0.1, "max_iterations": 0},
        {"epsilon": 0.1, "tolerance": 0},
        {"epsilon": 0.1, "method": "unknown"},
    ],
)
def test_invalid_solver_options(options):
    with pytest.raises(ValueError):
        sinkhorn(np.ones(1), np.ones(1), np.zeros((1, 1)), **options)


@pytest.mark.parametrize("p", [np.ones((1, 2)), np.array([[float("nan")]]), np.array([[-1.0]])])
def test_invalid_plan(p):
    with pytest.raises(ValueError):
        round_plan(p, np.ones(1), np.ones(1))


def test_invalid_support():
    with pytest.raises(ValueError):
        monotone_w2_squared(np.array([float("inf")]), np.zeros(1), np.ones(1), np.ones(1))
