import unittest
import numpy as np
from scipy.special import gammaincinv
from src.variance_interval import gaussian_variance_interval, wilson_interval


class VarianceIntervalTests(unittest.TestCase):
    def test_independent_quantile_oracle(self):
        x = [-2.0, -1.0, 0.0, 1.0, 2.0]
        ci = gaussian_variance_interval(x)
        assert ci is not None
        self.assertAlmostEqual(ci.low, 10 / (2 * gammaincinv(2, 0.95)), places=12)
        self.assertAlmostEqual(ci.high, 10 / (2 * gammaincinv(2, 0.05)), places=12)

    def test_shift_scale_and_permutation_invariants(self):
        rng = np.random.default_rng(123)
        for _ in range(20):
            x = rng.normal(size=30) * 0.1
            a = gaussian_variance_interval(x.tolist())
            b = gaussian_variance_interval((x[::-1] * 2 + 3).tolist())
            assert a is not None and b is not None
            self.assertAlmostEqual(b.low, 4 * a.low, places=11)
            self.assertAlmostEqual(b.high, 4 * a.high, places=11)

    def test_wider_confidence_and_clipping(self):
        x = [-0.5, 0.2, 0.3, 0.0]
        a = gaussian_variance_interval(x, 0.8)
        b = gaussian_variance_interval(x, 0.95)
        assert a is not None and b is not None
        self.assertLess(b.low, a.low)
        self.assertGreater(b.high, a.high)
        c = gaussian_variance_interval([-3, 3])
        assert c is not None
        self.assertEqual(c.high, 16)

    def test_zero_and_abstention(self):
        c = gaussian_variance_interval([1, 1, 1])
        assert c is not None
        self.assertEqual((c.low, c.high), (0, 0))
        self.assertIsNone(gaussian_variance_interval([-1e4, 1e4]))

    def test_invalid_inputs(self):
        for x in [[], [1], [1, float("nan")], [1, float("inf")], [1e308, -1e308]]:
            with self.assertRaises(ValueError):
                gaussian_variance_interval(x)
        for c in [0, 0.49, 1, float("nan")]:
            with self.assertRaises(ValueError):
                gaussian_variance_interval([0, 1], c)

    def test_wilson(self):
        lo, hi = wilson_interval(90, 100)
        self.assertAlmostEqual(lo, 0.8256343384950866, places=10)
        self.assertAlmostEqual(hi, 0.9447708629393249, places=10)
        for a, b in [(1, 0), (-1, 2), (3, 2)]:
            with self.assertRaises(ValueError):
                wilson_interval(a, b)
