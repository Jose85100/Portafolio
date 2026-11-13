from __future__ import annotations

import numpy as np
import unittest

from src.dependent_interval import (
    gls_chisquare_interval,
    iid_chisquare_interval,
    paired_chebyshev_interval,
    pair_variance_coefficient,
)


class DependentIntervalTests(unittest.TestCase):
 def test_pair_estimator_corrects_known_ar1_persistence(self) -> None:
    rng = np.random.default_rng(20261103)
    rho, variance, n = 0.9, 2.0, 150_000
    x = np.empty(n)
    x[0] = rng.normal(0, variance**0.5)
    eps = rng.normal(0, (variance * (1 - rho**2)) ** 0.5, n - 1)
    for i in range(1, n):
        x[i] = rho * x[i - 1] + eps[i - 1]
    raw = float(np.mean(np.diff(x) ** 2) / 2)
    corrected = raw / (1 - rho)
    self.assertLess(abs(raw - variance * (1 - rho)), 0.025)
    self.assertLess(abs(corrected - variance), 0.25)


 def test_pair_variance_coefficient_matches_closed_form_at_rho_zero(self) -> None:
    n = 20
    m = n - 1
    self.assertAlmostEqual(pair_variance_coefficient(n, 0.0), (3 * m - 1) / (m * m))


 def test_paired_interval_has_nonzero_width_and_contains_point_estimate(self) -> None:
    x = np.random.default_rng(11).normal(size=64)
    result = paired_chebyshev_interval(x, 0.0)
    self.assertIsNotNone(result.low)
    self.assertIsNotNone(result.high)
    self.assertLessEqual(result.low, result.estimate)
    self.assertLessEqual(result.estimate, result.high)


 def test_gls_whitening_matches_dense_gls_residual_variance(self) -> None:
    rng = np.random.default_rng(18)
    n, rho = 30, 0.7
    x = np.empty(n)
    variance = 1.5**2
    x[0] = rng.normal(4.0, variance**0.5)
    eps = rng.normal(0, variance**0.5 * (1 - rho**2) ** 0.5, n - 1)
    for i in range(1, n):
        x[i] = 4 + rho * (x[i - 1] - 4) + eps[i - 1]
    result = gls_chisquare_interval(x, rho)
    # Independent dense GLS construction on covariance R_ij=rho**|i-j|.
    index = np.arange(n)
    covariance = rho ** np.abs(index[:, None] - index[None, :])
    inverse = np.linalg.inv(covariance)
    ones = np.ones(n)
    mean = float(ones @ inverse @ x / (ones @ inverse @ ones))
    resid = x - mean
    dense_variance = float(resid @ inverse @ resid / (n - 1))
    self.assertAlmostEqual(result.estimate, dense_variance, delta=1e-12)


 def test_exact_gls_interval_contains_estimate(self) -> None:
    x = np.random.default_rng(23).normal(size=64)
    result = gls_chisquare_interval(x, -0.2)
    self.assertIsNotNone(result.low)
    self.assertIsNotNone(result.high)
    self.assertLessEqual(result.low, result.estimate)
    self.assertLessEqual(result.estimate, result.high)


 def test_iid_baseline_rejects_bad_data_and_confidence(self) -> None:
    with self.assertRaises(ValueError):
        iid_chisquare_interval([1.0, float("nan"), 3.0])
    with self.assertRaises(ValueError):
        iid_chisquare_interval([1.0, 2.0, 3.0], 1.0)


 def test_rho_outside_stationary_domain_is_rejected(self) -> None:
    for rho in [-1.0, 1.0, float("nan")]:
     with self.subTest(rho=rho), self.assertRaises(ValueError):
        pair_variance_coefficient(10, rho)


 def test_insufficient_and_nonfinite_series_rejected(self) -> None:
    with self.assertRaises(ValueError):
        paired_chebyshev_interval([1.0, 2.0], 0.2)
    with self.assertRaises(ValueError):
        gls_chisquare_interval([1.0, 2.0, float("inf")], 0.2)


if __name__ == "__main__":
    unittest.main()
