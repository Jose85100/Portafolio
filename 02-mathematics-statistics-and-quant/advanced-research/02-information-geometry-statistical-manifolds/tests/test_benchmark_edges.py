import numpy as np
import pytest
from src.benchmark import wilson
from src.geometry import fisher_rao, geodesic
from src.testing import permutation_test


def test_wilson_endpoints_do_not_create_negative_errorbars():
    low, high = wilson(0, 100)
    assert low == 0 and 0 < high < 1
    low, high = wilson(100, 100)
    assert high == 1 and 0 < low < 1


def test_zero_support_geodesic():
    a = np.array([1.0, 0.0, 0.0])
    b = np.array([0.0, 1.0, 0.0])
    for t in [0, 0.25, 0.5, 0.75, 1]:
        assert fisher_rao(a, geodesic(a, b, t)) == pytest.approx(t * np.pi, abs=1e-12)


def test_category_permutation_invariance():
    a = np.array([50.0, 4.0, 1.0, 0.0])
    b = np.array([40.0, 9.0, 5.0, 1.0])
    # Geometry invariance is deterministic; RNG category order can change sampled partitions.
    assert fisher_rao(a / a.sum(), b / b.sum()) == pytest.approx(
        fisher_rao(a[::-1] / a.sum(), b[::-1] / b.sum())
    )
    r = permutation_test(a, b, 99, 2)
    assert r["p_fr"] == r["p_hellinger"]
