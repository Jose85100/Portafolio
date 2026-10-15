from fractions import Fraction

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.guard import TailUnderflowError, exact_tail, guarded_tail
from src.sources import legacy, oracle


def test_representable_es_preserved() -> None:
    x, p = [1e308, 0.0], [1e-300, 1e300]
    assert legacy.weighted_tail(x, 0.975, p).es == 0
    result = guarded_tail(x, 0.975, p)
    assert result.backend == "fraction" and result.fallback_reason
    assert result.es > 0 and result.es == float(oracle.exact_es(x, p, 0.975))
    assert not result.output_rounds_to_zero


def test_explicit_rejection_and_budget() -> None:
    for kwargs in [{"policy": "raise"}, {"max_exact_scenarios": 1}]:
        with pytest.raises(TailUnderflowError):
            guarded_tail([1e308, 0], weights=[1e-300, 1e300], **kwargs)


def test_final_nonrepresentable_output_is_flagged() -> None:
    tiny = float(np.nextafter(0.0, 1.0))
    result = guarded_tail([0, tiny], 0.5, [3, 1])
    assert result.exact_es == Fraction(tiny) / 2
    assert result.es == 0 and result.output_rounds_to_zero


def test_global_error_state_restored() -> None:
    original = np.geterr()
    guarded_tail([1e308, 0], weights=[1e-300, 1e300])
    assert np.geterr() == original
    with pytest.raises(TailUnderflowError):
        guarded_tail([1e308, 0], weights=[1e-300, 1e300], policy="raise")
    assert np.geterr() == original


def test_fast_path_parity() -> None:
    result = guarded_tail([0, 100], weights=[99, 1])
    assert result.backend == "float64" and result.es == legacy.weighted_tail([0, 100], weights=[99, 1]).es
    assert result.exact_es is None and result.fallback_reason is None


@pytest.mark.parametrize("alpha", [0, 1, -1, float("nan"), float("inf")])
def test_invalid_alpha(alpha: float) -> None:
    for function in [guarded_tail, exact_tail]:
        with pytest.raises(ValueError):
            function([1, 2], alpha)


@pytest.mark.parametrize(
    "x,p",
    [
        ([], None),
        ([[1]], None),
        ([float("nan")], None),
        ([1, 2], [1]),
        ([1], [0]),
        ([1, 2], [-1, 2]),
        ([1], [float("inf")]),
    ],
)
def test_invalid_distribution(x: object, p: object) -> None:
    for function in [guarded_tail, exact_tail]:
        with pytest.raises((ValueError, TypeError)):
            function(x, weights=p)


def test_invalid_policy() -> None:
    with pytest.raises(ValueError):
        guarded_tail([1, 2], policy="ignore")  # type: ignore[arg-type]
    for cap in [0, -1, True, 1.5]:
        with pytest.raises(ValueError):
            guarded_tail([1, 2], max_exact_scenarios=cap)  # type: ignore[arg-type]


@settings(max_examples=100, derandomize=True, deadline=None)
@given(st.lists(st.tuples(st.integers(-100, 100), st.integers(1, 20)), min_size=1, max_size=20))
def test_exact_oracle_and_properties(rows: list[tuple[int, int]]) -> None:
    x, p = [float(v) for v, _ in rows], [float(w) for _, w in rows]
    result = exact_tail(x, 0.975, p)
    assert result.exact_es == oracle.exact_es(x, p, 0.975)
    assert exact_tail([v + 7 for v in x], 0.975, p).exact_es == result.exact_es + 7
    assert exact_tail([v * 3 for v in x], 0.975, p).exact_es == result.exact_es * 3
    assert exact_tail(x[::-1], 0.975, p[::-1]).exact_es == result.exact_es


def test_exact_tail_edge_cases() -> None:
    assert exact_tail([-5]).es == -5
    assert exact_tail([0, 100, 1e9], weights=[99, 1, 0]).var == 0
    assert exact_tail([1, 2], 0.5).var == 1


@settings(max_examples=100, derandomize=True, deadline=None)
@given(st.lists(st.integers(-1000, 1000), min_size=2, max_size=40))
def test_guarded_ordinary_parity(values: list[int]) -> None:
    result = guarded_tail(values, 0.975)
    assert result.backend == "float64"
    assert result.es == legacy.weighted_tail(values, 0.975).es
