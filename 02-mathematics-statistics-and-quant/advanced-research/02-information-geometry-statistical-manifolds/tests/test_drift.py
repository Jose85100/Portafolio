import math
import mpmath as mp
import numpy as np
import pytest
from hypothesis import given, strategies as st
from scipy.stats import wasserstein_distance, ks_2samp
from scipy.stats import binom
from src.drift import normal_fr, calibrate, scores, sample, rank_threshold


@given(st.floats(-10, 10), st.floats(0.1, 10), st.floats(-10, 10), st.floats(0.1, 10))
def test_normal_geometry(m, s, u, v):
    d = normal_fr(m, s, u, v)
    assert d >= 0
    assert d == pytest.approx(normal_fr(u, v, m, s), abs=1e-12)
    assert normal_fr(m, s, m, s) == 0
    assert normal_fr(m, s, m, v) == pytest.approx(math.sqrt(2) * abs(math.log(s / v)), abs=1e-12)
    assert d == pytest.approx(normal_fr(2 * m + 3, 2 * s, 2 * u + 3, 2 * v), abs=1e-12)


def test_oracle():
    with mp.workdps(80):
        for m, s, u, v in [(0, 1, 1e-12, 1), (0, 1, 0.8, 1), (0, 1, 0, 1.6), (2, 0.1, -3, 4)]:
            z = ((mp.mpf(m) - u) ** 2 + 2 * (mp.mpf(s) - v) ** 2) / (4 * mp.mpf(s) * v)
            ref = float(mp.sqrt(2) * mp.acosh(1 + z))
            assert normal_fr(m, s, u, v) == pytest.approx(ref, abs=1e-12)


@pytest.mark.parametrize("params", [(0, 0, 1, 1), (np.nan, 1, 0, 1), (0, 1e9, 0, 1), (1e9, 1, 0, 1)])
def test_invalid_parameters(params):
    with pytest.raises(ValueError):
        normal_fr(*params)


@pytest.mark.parametrize("a", [[1, 1, 1, 1], [1, 2, 3], [1, 2, 3, np.nan], [[1, 2, 3, 4]], [1e9, 2, 3, 4]])
def test_bad_samples(a):
    with pytest.raises(ValueError):
        sample(np.array(a))


def test_matched_lengths():
    with pytest.raises(ValueError):
        scores(np.arange(4.0), np.arange(5.0))


def test_baselines_and_no_input_mutation():
    rng = np.random.default_rng(81)
    a = rng.normal(size=16)
    b = rng.normal(0.5, size=16)
    original = a.copy()
    observed = scores(a, b)
    assert observed[1] == ks_2samp(a, b).statistic
    assert observed[2] == pytest.approx(wasserstein_distance(a, b) / a.std())
    cal = rng.normal(size=(39, 16))
    detector = calibrate(a, cal, 0.05)
    values, alarms = detector.predict(b)
    np.testing.assert_allclose(observed, values)
    np.testing.assert_array_equal(alarms, values > detector.thresholds)
    np.testing.assert_array_equal(a, original)
    assert not detector.reference.flags.writeable


def test_rank_guarantee_by_exhaustive_leave_one_out():
    values = np.arange(60.0).reshape(20, 3)
    for alpha in [0.05, 0.1, 0.2]:
        rejects = 0
        for i in range(20):
            threshold = rank_threshold(np.delete(values, i, axis=0), alpha)
            rejects += int(np.any(values[i] > threshold))
        assert rejects <= alpha * 20 + 1e-12


def test_tiny_calibration_conservative():
    assert np.isinf(rank_threshold(np.ones((1, 3)), 0.05)).all()


@pytest.mark.parametrize(
    "values,alpha",
    [(np.ones((3, 2)), 0.05), (np.array([[np.nan, 0, 1]]), 0.05), (np.ones((3, 3)), 0), (np.ones(3), 0.1)],
)
def test_bad_rank(values, alpha):
    with pytest.raises(ValueError):
        rank_threshold(values, alpha)


def test_bad_calibration():
    with pytest.raises(ValueError):
        calibrate(np.arange(4.0), np.ones((3, 5)))


def test_projection_blind_spot():
    a = np.linspace(-1, 1, 128)
    a = (a - a.mean()) / a.std()
    b = np.tile([-1.0, 1.0], 64)
    values = scores(a, b)
    assert values[0] < 1e-12
    assert values[1] > 0.1 and values[2] > 0.1


def test_pac_rank_bounds_calibration_failure_probability():
    b = 399
    values = np.tile(np.arange(b, dtype=float)[:, None], (1, 3))
    thresholds = rank_threshold(values, 0.05, 0.05)
    rank = int(thresholds[0]) + 1
    assert binom.sf(rank - 1, b, 0.95) <= 0.05 / 3
    assert np.all(thresholds >= rank_threshold(values, 0.05))
    with pytest.raises(ValueError):
        rank_threshold(values, 0.05, 0)
