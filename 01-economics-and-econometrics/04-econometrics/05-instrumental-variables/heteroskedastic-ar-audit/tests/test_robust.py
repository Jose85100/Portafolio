import unittest

import numpy as np
from scipy.stats import chi2

from src.baseline import ar_pvalue
from src.robust import robust_ar, sample


class RobustTests(unittest.TestCase):
    def test_sandwich_matrix_oracle(self):
        y, x, z = sample(4, 80, True)
        r = y - x
        design = np.column_stack([np.ones(len(z)), z])
        bread = np.linalg.inv(design.T @ design)
        b = bread @ design.T @ r
        e = r - design @ b
        h = np.sum((design @ bread) * design, axis=1)
        for kind in ["HC1", "HC3"]:
            weights = (
                e**2 * len(z) / (len(z) - 2) if kind == "HC1" else e**2 / (1 - h) ** 2
            )
            cov = bread @ (design.T @ (weights[:, None] * design)) @ bread
            self.assertAlmostEqual(
                robust_ar(y, x, z, 1, kind),
                chi2.sf(b[1] ** 2 / cov[1, 1], 1),
                places=12,
            )

    def test_properties(self):
        for seed in range(30):
            y, x, z = sample(seed, 100, True)
            for kind in ["HC1", "HC3"]:
                p = robust_ar(y, x, z, 1, kind)
                self.assertAlmostEqual(
                    p, robust_ar(y + 9, x - 2, z * -3 + 7, 1, kind), places=11
                )
                self.assertTrue(0 <= p <= 1)

    def test_weakness_invariance_at_true_null(self):
        for seed in range(20):
            weak = sample(seed, 100, True, 0)
            strong = sample(seed, 100, True, 10)
            self.assertAlmostEqual(
                robust_ar(*weak, 1), robust_ar(*strong, 1), places=12
            )

    def test_contracts(self):
        a = np.arange(10, dtype=float)
        for kind in ["BAD"]:
            with self.assertRaises(ValueError):
                robust_ar(a, a, a, 1, kind)
        with self.assertRaises(ValueError):
            robust_ar(a, a, a, float("nan"))
        with self.assertRaises(ValueError):
            robust_ar(a, a, np.ones(10), 1)
        with self.assertRaises(ValueError):
            robust_ar(a, a, a[:-1], 1)
        with self.assertRaises(ValueError):
            sample(0, 3, True)

    def test_leverage_and_nonfinite(self):
        a = np.arange(10, dtype=float)
        z = np.zeros(10)
        z[-1] = 1
        with self.assertRaises(ValueError):
            robust_ar(a, a, z, 1)
        with self.assertRaises(ValueError):
            robust_ar(a * float("nan"), a, a, 1)
        with self.assertRaises(ValueError):
            robust_ar(a[:, None], a, a, 1)
        with self.assertRaises(ValueError):
            ar_pvalue(a, a, a, float("nan"))
        self.assertEqual(ar_pvalue(a, a, a, 1), 1)

    def test_degenerate_residual(self):
        z = np.arange(20, dtype=float)
        self.assertEqual(robust_ar(z, z, z, 1), 1)
        self.assertEqual(robust_ar(z, z, z, 0), 0)

    def test_size_smoke(self):
        r = [robust_ar(*sample(seed, 300, True), 1) < 0.05 for seed in range(300)]
        self.assertLess(abs(np.mean(r) - 0.05), 0.04)

    def test_baseline_not_robust(self):
        data = sample(2, 200, True)
        self.assertNotAlmostEqual(ar_pvalue(*data, 1), robust_ar(*data, 1), places=3)


if __name__ == "__main__":
    unittest.main()
