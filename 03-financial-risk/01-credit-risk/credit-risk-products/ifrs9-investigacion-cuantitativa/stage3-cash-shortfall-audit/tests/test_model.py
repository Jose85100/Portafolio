import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.baseline import legacy_ecl
from src.model import scenario_shortfall, shortfall


def test_worked_example_and_baseline() -> None:
    g = np.array([100.0])
    new = shortfall(g, [[60]], [2], 0.1)
    assert new[0] == pytest.approx(100 - 60 / 1.1**2)
    old = legacy_ecl(g, new / g, 0.05, 5, 0.1)
    assert old[0] < new[0]


@settings(max_examples=100, derandomize=True)
@given(st.integers(0, 10000), st.integers(0, 100), st.integers(0, 20))
def test_bounds_delay_and_scale(gross: int, percent: int, lag: int) -> None:
    recovery = float(gross) * percent / 100
    result = shortfall([float(gross)], [[recovery]], [lag], 0.1)[0]
    assert 0 <= result <= gross + 1e-10
    later = shortfall([float(gross)], [[recovery]], [lag + 1], 0.1)[0]
    assert later >= result
    assert shortfall([gross * 2.0], [[recovery * 2]], [lag], 0.1)[0] == pytest.approx(result * 2)


@settings(max_examples=100, derandomize=True)
@given(st.integers(0, 100), st.integers(0, 100))
def test_scenario_linearity(a: int, b: int) -> None:
    out = scenario_shortfall([100], [[[float(a)]], [[float(b)]]], [2], 0.1, [0.3, 0.7])
    direct = shortfall([100], [[0.3 * a + 0.7 * b]], [2], 0.1)
    assert out == pytest.approx(direct)


def test_full_delayed_recovery_is_not_zero_loss() -> None:
    assert shortfall([100], [[100]], [1], 0.1)[0] == pytest.approx(100 / 11)
    assert shortfall([100], [[100]], [0], 0.1)[0] == 0
    assert shortfall([100], [[0]], [5], 0.1)[0] == 100


def test_tiny_delay_numerical_stability() -> None:
    result = shortfall([100], [[100]], [1], 1e-18)[0]
    assert result == pytest.approx(1e-16, rel=1e-12, abs=0)
    assert 100 - 100 / (1 + 1e-18) == 0  # subtractive ablation loses it


@pytest.mark.parametrize(
    "gross,cash,times,rate",
    [
        ([], [], [1], 0.1),
        ([-1], [[0]], [1], 0.1),
        ([float("nan")], [[0]], [1], 0.1),
        ([100], [[-1]], [1], 0.1),
        ([100], [[101]], [1], 0.1),
        ([100], [[0, 1]], [1], 0.1),
        ([100], [[0]], [-1], 0.1),
        ([100], [[0]], [], 0.1),
        ([100], [[0]], [float("inf")], 0.1),
        ([100], [[0]], [1], -0.1),
        ([100], [[0]], [1], float("nan")),
    ],
)
def test_invalid_inputs(gross: list, cash: list, times: list, rate: float) -> None:
    with pytest.raises(ValueError):
        shortfall(gross, cash, times, rate)


@pytest.mark.parametrize(
    "cash,weights", [([], []), ([[[1]]], [-1]), ([[[1]]], [0.5]), ([[[1]]], [float("nan")]), ([[1]], [1])]
)
def test_bad_scenarios(cash: list, weights: list) -> None:
    with pytest.raises(ValueError):
        scenario_shortfall([100], cash, [1], 0.1, weights)
