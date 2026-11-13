from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.gauge import (
    analytic_jacobian,
    best_rank_one,
    canonicalize,
    finite_difference_jacobian,
    fisher_information,
    gauge_tangent,
    mean_matrix,
    spectral_certificate,
)


@given(
    st.lists(st.floats(-5, 5, allow_nan=False, allow_infinity=False), min_size=2, max_size=6),
    st.lists(st.floats(-5, 5, allow_nan=False, allow_infinity=False), min_size=2, max_size=6),
    st.floats(0.01, 100, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=50, deadline=None)
def test_scale_orbit_preserves_prediction(u_values: list[float], v_values: list[float], scale: float) -> None:
    u = np.asarray(u_values)
    v = np.asarray(v_values)
    np.testing.assert_allclose(mean_matrix(scale * u, v / scale), mean_matrix(u, v), atol=1e-12)


def test_analytic_matches_finite_difference() -> None:
    u = np.array([0.4, -1.2, 0.7])
    v = np.array([1.1, -0.2])
    analytic = analytic_jacobian(u, v)
    numeric = finite_difference_jacobian(u, v)
    np.testing.assert_allclose(analytic, numeric, rtol=1e-9, atol=1e-10)


def test_exactly_one_null_direction_and_tangent() -> None:
    u = np.array([1.0, -0.4, 0.2])
    v = np.array([0.3, 1.4])
    jacobian = analytic_jacobian(u, v)
    certificate = spectral_certificate(fisher_information(jacobian, 0.2))
    assert certificate.nullity == 1
    assert certificate.rank == u.size + v.size - 1
    np.testing.assert_allclose(jacobian @ gauge_tangent(u, v), 0.0, atol=1e-14)


def test_degenerate_case_has_extra_nullity() -> None:
    jacobian = analytic_jacobian(np.zeros(3), np.array([1.0, 2.0]))
    assert spectral_certificate(fisher_information(jacobian, 1.0)).nullity == 2


def test_canonicalize_is_orbit_invariant_and_balanced() -> None:
    u = np.array([1.0, -2.0, 0.5])
    v = np.array([-0.7, 0.3])
    reference = canonicalize(u, v)
    transformed = canonicalize(-1e5 * u, v / -1e5)
    np.testing.assert_allclose(reference[0], transformed[0], atol=1e-11)
    np.testing.assert_allclose(reference[1], transformed[1], atol=1e-11)
    assert np.linalg.norm(reference[0]) == pytest.approx(np.linalg.norm(reference[1]))


def test_best_rank_one_exact_recovery_of_product() -> None:
    u = np.array([1.0, 2.0, -1.0])
    v = np.array([0.5, -0.25])
    fitted = best_rank_one(mean_matrix(u, v))
    np.testing.assert_allclose(mean_matrix(*fitted), mean_matrix(u, v), atol=1e-12)


@pytest.mark.parametrize(
    ("call", "match"),
    [
        (lambda: mean_matrix(np.array([np.nan]), np.array([1.0])), "finite vector"),
        (lambda: finite_difference_jacobian(np.ones(2), np.ones(2), 0.0), "step"),
        (lambda: fisher_information(np.eye(2), 0.0), "noise_std"),
        (lambda: spectral_certificate(np.ones((2, 3))), "square"),
        (lambda: spectral_certificate(np.array([[1.0, 2.0], [0.0, 1.0]])), "symmetric"),
        (lambda: canonicalize(np.zeros(2), np.ones(2)), "nonzero"),
        (lambda: best_rank_one(np.zeros((2, 2))), "degenerate"),
    ],
)
def test_invalid_inputs(call: object, match: str) -> None:
    with pytest.raises(ValueError, match=match):
        call()  # type: ignore[operator]
