import math

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.ou import (
    Transition,
    diagnostics,
    euler_transition,
    exact_transition,
    finite_variance,
    simulate,
    stationary_variance,
)
from src.reference import matrix_transition


@pytest.mark.parametrize("kappa,dt", [(1, 1e-12), (0.01, 0.1), (1, 1), (2, 2.5), (1, 20)])
def test_matrix_oracle(kappa, dt):
    a, b = exact_transition(kappa, 0.7, dt), matrix_transition(kappa, 0.7, dt)
    assert a.phi == pytest.approx(b.phi, rel=1e-12, abs=1e-14)
    assert a.innovation_variance == pytest.approx(b.innovation_variance, rel=1e-12)


@settings(max_examples=80, derandomize=True, deadline=None)
@given(k=st.floats(0.01, 5), s=st.floats(0, 3), dt=st.floats(0.001, 2))
def test_semigroup(k, s, dt):
    one = exact_transition(k, s, dt)
    two = exact_transition(k, s, 2 * dt)
    assert two.phi == pytest.approx(one.phi**2, rel=1e-12)
    assert two.innovation_variance == pytest.approx(
        one.innovation_variance * (1 + one.phi**2), rel=1e-12, abs=1e-15
    )


@settings(max_examples=60, derandomize=True, deadline=None)
@given(k=st.floats(0.02, 4), s=st.floats(0.001, 4), dt=st.floats(0.001, 2))
def test_stationary_identity(k, s, dt):
    t = exact_transition(k, s, dt)
    assert stationary_variance(t) == pytest.approx(s * s / (2 * k), rel=2e-11)


@pytest.mark.parametrize(
    "k,s,dt",
    [
        (0, 1, 1),
        (-1, 1, 1),
        (1, -1, 1),
        (1, 1, 0),
        (math.nan, 1, 1),
        (1, math.inf, 1),
        (101, 1, 1),
        (1, 101, 1),
        (1, 1, 101),
        (1e-14, 1, 1),
    ],
)
def test_invalid_parameters(k, s, dt):
    with pytest.raises(ValueError):
        exact_transition(k, s, dt)


def test_brownian_limit_and_zero_diffusion():
    assert exact_transition(1, 2, 1e-12).innovation_variance == pytest.approx(4e-12, rel=2e-12)
    assert exact_transition(1, 0, 1).innovation_variance == 0
    assert np.array_equal(simulate(exact_transition(1, 0, 1), np.ones((2, 4))), np.zeros((2, 4)))


def test_finite_variance_and_euler_stability():
    assert finite_variance(Transition(1, 2), 3) == 6
    assert finite_variance(Transition(-1, 2), 3) == 6
    assert finite_variance(Transition(0.5, 1), 0) == 0
    assert stationary_variance(euler_transition(1, 1, 1)) == 1
    assert stationary_variance(exact_transition(1, 1, 1)) == pytest.approx(0.5)
    for dt in (2, 2.5):
        with pytest.raises(ValueError):
            stationary_variance(euler_transition(1, 1, dt))


@pytest.mark.parametrize(
    "t,steps",
    [
        (Transition(0, -1), 2),
        (Transition(math.nan, 1), 1),
        (Transition(0, math.inf), 1),
        (Transition(1e200, 1), 3),
        (Transition(0, 1), -1),
        (Transition(0, 1), 1.2),
        (Transition(0, 1), True),
    ],
)
def test_invalid_variance(t, steps):
    with pytest.raises((ValueError, OverflowError)):
        finite_variance(t, steps)


def test_stationary_bad_q():
    with pytest.raises(ValueError):
        stationary_variance(Transition(0.5, -1))


def test_simulate_recurrence_and_seed():
    z = np.random.default_rng(7).normal(size=(3, 8))
    t = exact_transition(0.5, 1, 1)
    y = simulate(t, z)
    assert np.array_equal(y, simulate(t, z))
    assert np.all(y[:, 0] == 0)
    assert np.allclose(y[:, 1:], t.phi * y[:, :-1] + math.sqrt(t.innovation_variance) * z[:, 1:])
    stationary = simulate(t, z, stationary=True)
    assert np.allclose(stationary[:, 0], z[:, 0])


@pytest.mark.parametrize("z", [np.ones(4), np.empty((0, 3)), np.array([[math.nan]])])
def test_simulate_bad_inputs(z):
    with pytest.raises(ValueError):
        simulate(Transition(0.5, 1), z)


def test_diagnostics_no_clipping():
    x = np.array([[1, 2, 4, 8], [1, -1, 1, -1], [0, 0, 0, 0]], dtype=float)
    _, phi, rates = diagnostics(x, 1)
    assert phi[0] == 2
    assert phi[1] == -1
    assert np.isnan(phi[2])
    assert np.isnan(rates).all()
    _, phi2, rates2 = diagnostics(np.array([[8, 4, 2, 1]], dtype=float), 1)
    assert phi2[0] == 0.5
    assert rates2[0] == pytest.approx(math.log(2))


@pytest.mark.parametrize(
    "x,dt", [(np.ones(4), 1), (np.ones((2, 2)), 1), (np.ones((2, 3)), 0), (np.ones((2, 3)), math.nan)]
)
def test_diagnostics_bad_inputs(x, dt):
    with pytest.raises(ValueError):
        diagnostics(x, dt)


def test_population_variance_nonidentification():
    for k in (1, 0.5, 0.2, 0.1):
        slowing = exact_transition(k, 1, 1)
        noise = exact_transition(1, math.sqrt(1 / k), 1)
        assert stationary_variance(slowing) == pytest.approx(stationary_variance(noise))
    assert exact_transition(0.1, 1, 1).phi - exact_transition(1, math.sqrt(10), 1).phi > 0.5


@pytest.mark.parametrize("k,s,dt", [(0, 1, 1), (1, -1, 1), (1, 1, 0), (1, 1, 21), (math.nan, 1, 1)])
def test_oracle_limits(k, s, dt):
    with pytest.raises(ValueError):
        matrix_transition(k, s, dt)
