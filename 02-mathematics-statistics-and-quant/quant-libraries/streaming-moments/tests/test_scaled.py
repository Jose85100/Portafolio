import math
import random
import unittest
from src.scaled import scaled_moments
from src.moments import summarize


class ScaledTests(unittest.TestCase):
    def test_extremes(self):
        for unit, e, status in [
            (1e200, 665, "variance_overflow"),
            (1e-200, -665, "variance_underflow"),
        ]:
            x = [unit, 2 * unit, 3 * unit, 4 * unit]
            out = scaled_moments(iter(x), e)
            self.assertEqual(out.status, status)
            self.assertAlmostEqual(out.std / unit, math.sqrt(1.25), places=14)
            self.assertIsNone(out.variance)
        self.assertFalse(math.isfinite(summarize([1e200, 2e200]).variance()))
        self.assertEqual(summarize([1e-200, 2e-200]).variance(), 0.0)

    def test_sensitivity_and_properties(self):
        rng = random.Random(20261030)
        for _ in range(50):
            x = [float(rng.randrange(-100, 101)) for _ in range(32)]
            expected = summarize(x).variance()
            for e in [-100, 0, 100]:
                out = scaled_moments(x, e)
                self.assertEqual(out.status, "ok")
                self.assertAlmostEqual(out.variance, expected, places=10)
                self.assertAlmostEqual(out.std**2, expected, places=10)
        self.assertEqual(
            scaled_moments([1e200, 2e200], 0).status, "normalization_failure"
        )
        self.assertEqual(
            scaled_moments([1e-200, 2e-200], 0).status, "normalization_failure"
        )

    def test_edges(self):
        self.assertEqual(scaled_moments([0.0] * 4, 1000).variance, 0.0)
        for e in [1024, -1075, 1.5, True]:
            with self.assertRaises(ValueError):
                scaled_moments([1.0], e)
        for vals in [[], [float("inf")], [float("nan")]]:
            with self.assertRaises(ValueError):
                scaled_moments(vals, 0)
        with self.assertRaises(ValueError):
            scaled_moments([1.0], 0, 1)
        with self.assertRaises(ValueError):
            scaled_moments([1.0, 2.0], 0, 2)
        self.assertEqual(scaled_moments([1.0, 3.0], 0, 1).variance, 2.0)
        self.assertEqual(scaled_moments([1e308], -1074).status, "normalization_failure")

    def test_sample_sd_overflow(self):
        out = scaled_moments([-1.7e308, 1.7e308], 1023, 1)
        self.assertEqual(out.status, "std_overflow")
        self.assertIsNone(out.std)
        self.assertIsNone(out.variance)
