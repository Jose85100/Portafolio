import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.baselines import construction_es, historical_es, liquidity_es, historical_corrected_es
from src.oracle import lp_es
from src.tail import equal_mass_reference, weighted_tail


@pytest.mark.parametrize("alpha", [0, 1, -1, float("nan"), float("inf")])
def test_invalid_alpha(alpha):
    with pytest.raises(ValueError):
        weighted_tail([1, 2], alpha)


@pytest.mark.parametrize(
    "losses,weights",
    [
        ([], None),
        ([[1]], None),
        ([float("nan")], None),
        ([float("inf")], None),
        ([1, 2], [1]),
        ([1, 2], [-1, 2]),
        ([1], [0]),
        ([1], [float("nan")]),
    ],
)
def test_invalid_distribution(losses, weights):
    with pytest.raises(ValueError):
        weighted_tail(losses, weights=weights)


def test_discrete_counterexample():
    x = [0.0] * 99 + [100.0]
    assert weighted_tail(x).es == pytest.approx(40)
    assert historical_es(x, 0.975) == pytest.approx(1)
    assert construction_es(x, 0.975) == pytest.approx(40)
    assert lp_es(x) == pytest.approx(40)


def test_weighted_boundary_and_zero_mass():
    result = weighted_tail([0, 100, 1e9], weights=[99, 1, 0])
    assert result.var == 0
    assert result.es == pytest.approx(40)
    assert result.tail_mass == pytest.approx(0.025)


def test_singleton_constant_signed_and_extreme_alpha():
    for x in [[-5.0], [-2.0] * 10, [1.0, 2.0, 3.0]]:
        for a in [1e-12, 0.5, np.nextafter(1.0, 0.0)]:
            r = weighted_tail(x, float(a))
            assert min(x) - 1e-9 <= r.es <= max(x) + 1e-9
            assert r.es >= r.var - 1e-9
            assert r.tail_mass == pytest.approx(1 - a, rel=1e-10, abs=1e-15)


def test_weight_normalization_and_overflow_scaling():
    assert weighted_tail([1, 2], weights=[1e308, 1e308]).es == pytest.approx(2)
    assert weighted_tail([-1e300, 1e300], 0.5).es == pytest.approx(1e300)


vectors = st.lists(st.integers(-1000, 1000), min_size=1, max_size=40)
levels = st.sampled_from([0.5, 0.9, 0.95, 0.975, 0.99])


@settings(max_examples=100, derandomize=True, deadline=None)
@given(vectors, levels)
def test_reference_and_lp(x, alpha):
    r = weighted_tail(x, alpha)
    assert r.es == pytest.approx(equal_mass_reference(x, alpha), abs=1e-8)
    assert r.es == pytest.approx(lp_es(x, alpha), abs=1e-8)
    assert r.tail_mass == pytest.approx(1 - alpha, abs=1e-12)


@settings(max_examples=100, derandomize=True, deadline=None)
@given(vectors, levels, st.integers(-100, 100), st.integers(0, 10))
def test_translation_homogeneity_monotonicity(x, alpha, shift, factor):
    a = np.asarray(x, dtype=float)
    es = weighted_tail(a, alpha).es
    assert weighted_tail(a + shift, alpha).es == pytest.approx(es + shift, abs=1e-8)
    assert weighted_tail(a * factor, alpha).es == pytest.approx(es * factor, abs=1e-8)
    assert weighted_tail(a + np.arange(len(a)), alpha).es >= es - 1e-8
    assert weighted_tail(a[::-1], alpha).es == pytest.approx(es, abs=1e-8)


@settings(max_examples=100, derandomize=True, deadline=None)
@given(
    st.lists(
        st.tuples(st.integers(-100, 100), st.integers(-100, 100), st.integers(1, 100)),
        min_size=2,
        max_size=25,
    ),
    levels,
)
def test_weighted_lp_and_subadditivity(rows, alpha):
    x, y, p = np.asarray(rows, dtype=float).T
    es = weighted_tail(x, alpha, p).es
    assert es == pytest.approx(lp_es(x, alpha, p), abs=1e-8)
    assert weighted_tail(x + y, alpha, p).es <= es + weighted_tail(y, alpha, p).es + 1e-8


def test_lp_errors(monkeypatch):
    from types import SimpleNamespace

    import src.oracle

    monkeypatch.setattr(
        src.oracle, "linprog", lambda *a, **kw: SimpleNamespace(success=False, message="failure")
    )
    with pytest.raises(RuntimeError, match="failure"):
        lp_es([1, 2])


@settings(max_examples=100, derandomize=True, deadline=None)
@given(st.lists(st.integers(-1000, 1000), min_size=2, max_size=50), levels)
def test_actual_liquidity_baseline(x, alpha):
    assert weighted_tail(x, alpha).es == pytest.approx(liquidity_es(x, alpha), abs=1e-8)


def test_current_historical_api_matches_shared_fixtures():
    import csv
    from pathlib import Path
    path=Path(__file__).resolve().parents[3]/'07-financial-and-construction-risk-lab/tests/fixtures/tail_contract.csv'
    for row in csv.DictReader(path.open()):
        losses=list(map(float,row['losses'].split(';')))
        if len(losses)<2:continue
        assert historical_corrected_es(losses,float(row['alpha'])) == pytest.approx(float(row['es']),abs=1e-9)
    with pytest.raises(ValueError):historical_corrected_es([float('nan'),0],.95)
