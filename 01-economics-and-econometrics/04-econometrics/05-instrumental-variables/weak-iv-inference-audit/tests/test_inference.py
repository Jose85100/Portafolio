"""Algebra, invariance, contracts and finite-sample sanity checks."""

import unittest
import numpy as np
from scipy.stats import linregress
from src.inference import ar_pvalue, first_stage_f, sample, wald_pvalue


class InferenceTests(unittest.TestCase):
    def test_reduced_form(self):
        y, x, z = sample(12, 100, 1)
        self.assertAlmostEqual(
            ar_pvalue(y, x, z, 1), linregress(z, y - x).pvalue, places=12
        )

    def test_invariance(self):
        for seed in range(30):
            y, x, z = sample(seed, 100, 1)
            self.assertAlmostEqual(
                ar_pvalue(y, x, z, 1),
                ar_pvalue(y + 17, x - 2, z * -3 + 4, 1),
                places=11,
            )

    def test_zero_first_stage(self):
        y, x, z = sample(21, 80, 0)
        self.assertTrue(0 <= ar_pvalue(y, np.zeros_like(x), z, 1) <= 1)

    def test_bad_inputs(self):
        a = np.arange(6, dtype=float)
        for y, x, z in [
            (a[:-1], a, a),
            (a, a, np.ones(6)),
            (a * float("nan"), a, a),
            (a[:, None], a, a),
        ]:
            with self.assertRaises(ValueError):
                ar_pvalue(y, x, z, 1)
        with self.assertRaises(ValueError):
            ar_pvalue(a, a, a, float("nan"))

    def test_baseline_edge_contracts(self):
        a = np.arange(10, dtype=float)
        with self.assertRaises(ValueError):
            wald_pvalue(a, a, a, float("nan"))
        self.assertEqual(first_stage_f(np.ones(10), a), 0.0)

    def test_degenerate_null(self):
        z = np.arange(10, dtype=float)
        self.assertEqual(ar_pvalue(z, z, z, 1), 1)
        self.assertEqual(ar_pvalue(z, z, z, 0), 0)

    def test_reproducibility(self):
        for a, b in zip(sample(4, 100, 1), sample(4, 100, 1)):
            np.testing.assert_array_equal(a, b)
        with self.assertRaises(ValueError):
            sample(2, 3, 1)
        with self.assertRaises(ValueError):
            sample(2, 100, 1, rho=1)

    def test_size_and_exclusion(self):
        rates = [
            np.mean(
                [
                    ar_pvalue(*sample(seed, 150, 1, exclusion=e), 1) < 0.05
                    for seed in range(500)
                ]
            )
            for e in (0, 0.3)
        ]
        self.assertLess(abs(rates[0] - 0.05), 0.035)
        self.assertGreater(rates[1], 0.65)

    def test_baseline_and_relevance(self):
        y, x, z = sample(99, 100, 10)
        self.assertTrue(0 <= wald_pvalue(y, x, z, 1) <= 1)
        self.assertGreater(first_stage_f(x, z), 10)


if __name__ == "__main__":
    unittest.main()
