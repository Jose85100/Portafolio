import unittest

import numpy as np
from scipy.stats import linregress

from src.confounding import generate, lag_test, paired_intervention


class ConfoundingTests(unittest.TestCase):
    def test_reproducible_alignment_and_intervention(self):
        sample = generate(100, 0.3, 55)
        twin = generate(100, 0.3, 55)
        np.testing.assert_array_equal(sample.y, twin.y)
        np.testing.assert_allclose(paired_intervention(sample, 2) - sample.y, 0.6)
        null = generate(100, 0, 55)
        np.testing.assert_array_equal(paired_intervention(null, 2), null.y)
        # Xlag = .8*Zlag2 + independent ux; identical hidden draws across effect values.
        np.testing.assert_allclose(sample.y - null.y, 0.3 * sample.x_lag)

    def test_independent_univariate_oracle(self):
        s = generate(200, 0, 77)
        result = lag_test(s.y, s.x_lag)
        ref = linregress(s.x_lag, s.y)
        self.assertAlmostEqual(result.slope, ref.slope, places=12)
        self.assertAlmostEqual(result.standard_error, ref.stderr, places=12)
        self.assertAlmostEqual(result.p_value, ref.pvalue, places=12)
        self.assertAlmostEqual(
            result.f_statistic, (result.slope / result.standard_error) ** 2, places=9
        )

    def test_affine_covariance_and_control_residualization(self):
        s = generate(200, 0.3, 88)
        a = lag_test(s.y, s.x_lag, s.z_lag2)
        b = lag_test(2 * s.y + 7, 4 * s.x_lag - 2, s.z_lag2 + 9)
        self.assertAlmostEqual(a.p_value, b.p_value, places=11)
        self.assertAlmostEqual(b.slope, a.slope / 2, places=11)
        design = np.column_stack([np.ones(200), s.z_lag2])
        rx = s.x_lag - design @ np.linalg.lstsq(design, s.x_lag, rcond=None)[0]
        ry = s.y - design @ np.linalg.lstsq(design, s.y, rcond=None)[0]
        self.assertAlmostEqual(a.slope, float(rx @ ry / (rx @ rx)), places=12)

    def test_randomized_partial_regression_identity(self):
        rng = np.random.default_rng(918)
        for n in [30, 100]:
            for _ in range(5):
                controls = rng.normal(size=(n, 2))
                x = rng.normal(size=n) + controls[:, 0]
                y = 0.4 * x + controls[:, 1] + rng.normal(size=n)
                result = lag_test(y, x, controls)
                design = np.column_stack([np.ones(n), controls])
                rx = x - design @ np.linalg.lstsq(design, x, rcond=None)[0]
                ry = y - design @ np.linalg.lstsq(design, y, rcond=None)[0]
                self.assertAlmostEqual(
                    result.slope, float(rx @ ry / (rx @ rx)), places=11
                )
                self.assertAlmostEqual(
                    result.f_statistic,
                    (result.slope / result.standard_error) ** 2,
                    places=9,
                )

    def test_confusion_and_positive_effect_large_n(self):
        s = generate(10000, 0, 99)
        self.assertGreater(lag_test(s.y, s.x_lag).slope, 0.65)
        self.assertLess(abs(lag_test(s.y, s.x_lag, s.z_lag2).slope), 0.03)
        alt = generate(10000, 0.3, 100)
        self.assertLess(abs(lag_test(alt.y, alt.x_lag, alt.z_lag2).slope - 0.3), 0.03)

    def test_bad_inputs_and_degeneracy(self):
        with self.assertRaises(ValueError):
            generate(1, 0, 1)
        s = generate(20, 0, 1)
        for x, y, c in [
            (s.x_lag[:-1], s.y, None),
            (s.x_lag, s.y, np.zeros((3, 2))),
            (np.ones(20), s.y, None),
            (s.x_lag, s.y, np.full(20, np.nan)),
            (s.x_lag, np.zeros(20), None),
            (np.arange(2.0), np.arange(2.0), None),
        ]:
            with self.assertRaises(ValueError):
                lag_test(y, x, c)
        with self.assertRaises(ValueError):
            lag_test(s.y, s.x_lag, alpha=1)
        with self.assertRaises(ValueError):
            paired_intervention(s, np.inf)
