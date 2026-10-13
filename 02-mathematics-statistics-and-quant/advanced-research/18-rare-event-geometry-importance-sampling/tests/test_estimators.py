import math
import numpy as np
import pytest
from hypothesis import given, strategies as st
from scipy.integrate import quad
from scipy.special import logsumexp
from src.estimators import METHODS, estimate, log_weight, population_variance, proposal, truth


@pytest.mark.parametrize("a", [1.0, 2.0, 4.0, 8.0])
@pytest.mark.parametrize("method", METHODS)
def test_integral_is_unbiased(a, method):
    means, probs = proposal(a, method)

    def integrand(x):
        log_q = logsumexp(np.log(probs) - 0.5 * (x - means) ** 2) - 0.5 * math.log(2 * math.pi)
        return math.exp(log_q + float(log_weight(np.array([x]), a, method)[0]))

    integral = sum(
        quad(integrand, lo, hi, epsabs=1e-25)[0] for lo, hi in [(-np.inf, -a), (a, np.inf)]
    )
    assert integral == pytest.approx(truth(a), rel=1e-7, abs=1e-25)


@given(
    st.floats(min_value=-30, max_value=30, allow_nan=False),
    st.floats(min_value=0.1, max_value=8, allow_nan=False),
)
def test_mixture_symmetry(x, a):
    for method in ["balanced", "defensive"]:
        weights = log_weight(np.array([x, -x]), a, method)
        assert weights[0] == pytest.approx(weights[1], abs=1e-10)
        if method == "defensive":
            assert weights[0] <= math.log(10) + 1e-10


@pytest.mark.parametrize("a", [0, -1, 9, float("inf"), float("nan")])
def test_invalid_threshold(a):
    with pytest.raises(ValueError):
        truth(a)


@pytest.mark.parametrize("n", [0, 1, True, 2.5])
def test_invalid_sample_size(n):
    with pytest.raises(ValueError):
        estimate(4, n, 1, "balanced")


def test_unknown_method():
    with pytest.raises(ValueError):
        proposal(4, "unknown")


def test_reproducible():
    assert estimate(4, 2000, 123, "balanced") == estimate(4, 2000, 123, "balanced")


def test_zero_hits():
    result = estimate(8, 10, 123, "direct")
    assert result.mean == result.se == result.contribution_ess == 0


def test_population_variance_counterexample():
    assert population_variance(4, "single_tilt") > 1e9 * population_variance(4, "direct")
    assert population_variance(4, "balanced") < 0.01 * population_variance(4, "direct")


def test_fixed_seed_smoke_not_calibration():
    result = estimate(4, 20000, 20261013, "balanced")
    assert abs(result.mean - truth(4)) < 5 * result.se
    assert result.left_hits > 0 and result.right_hits > 0


@given(st.floats(min_value=0.1, max_value=8), st.floats(min_value=0, max_value=20))
def test_balanced_event_weight_bound(a, extra):
    x = np.array([a + extra, -a - extra])
    bound = math.log(2) - 0.5 * a * a
    assert np.all(log_weight(x, a, "balanced") <= bound + 1e-10)
