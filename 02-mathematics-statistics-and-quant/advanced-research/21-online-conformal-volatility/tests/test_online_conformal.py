import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from online_conformal import conformal_quantile, coverage, evaluate, simulate

class ConformalTests(unittest.TestCase):
    def test_order_statistic(self):
        self.assertEqual(conformal_quantile([1, 2, 3, 4], .2), 4)
    def test_invalid_alpha_and_empty(self):
        for a in (0, 1, -0.1):
            with self.assertRaises(ValueError): conformal_quantile([1], a)
        with self.assertRaises(ValueError): conformal_quantile([], .1)
    def test_coverage_exact(self):
        self.assertEqual(coverage(np.array([0., 2.]), np.array([-1., 1.]), np.array([1., 3.])).rate, 1.0)
    def test_bad_bounds(self):
        with self.assertRaises(ValueError): coverage(np.array([0.]), np.array([1.]), np.array([0.]))
    def test_constant_zero_and_seed(self):
        x = simulate(7, 50, 50)
        self.assertTrue(np.array_equal(x, simulate(7, 50, 50)))
        self.assertTrue(np.all(np.isfinite(list(evaluate(np.zeros(30), window=5).values()))))
    def test_scaling_reacts(self):
        x = simulate(9, 1000, 500, 3.)
        r = evaluate(x, window=100)
        self.assertGreater(r["rolling_postbreak_coverage"], r["fixed_postbreak_coverage"])

if __name__ == "__main__": unittest.main()
