import unittest
from itertools import product
import numpy as np
from src.moment_interval import bounded_kurtosis_interval


class MomentIntervalTests(unittest.TestCase):
    def test_exact_pair_moments(self):
        # Three-point law: mean0, variance1, Pearson fourth moment9.
        values = [-3.0, 0.0, 3.0]
        probabilities = [1 / 18, 8 / 9, 1 / 18]
        first = second = 0.0
        for i, j in product(range(3), repeat=2):
            w = (values[i] - values[j]) ** 2 / 2
            probability = probabilities[i] * probabilities[j]
            first += probability * w
            second += probability * w * w
        self.assertAlmostEqual(first, 1)
        self.assertAlmostEqual(second - first**2, 5)

    def test_exact_discrete_coverage(self):
        # Enumerate all 2^8 samples, exact Rademacher law; not Monte Carlo.
        covered = 0
        for sample in product([-1.0, 1.0], repeat=8):
            ci = bounded_kurtosis_interval(sample, kurtosis_bound=1, confidence=0.5)
            assert ci is not None
            covered += ci.low <= 1 <= ci.high
        self.assertGreaterEqual(covered / 256, 0.5)

    def test_pair_invariances_and_odd_tail(self):
        x = np.random.default_rng(4).normal(0, 0.1, 40)
        a = bounded_kurtosis_interval(x.tolist())
        b = bounded_kurtosis_interval((2 * x + 4).tolist())
        c = bounded_kurtosis_interval([*x.tolist(), 99999.0])
        assert a is not None and b is not None and c is not None
        self.assertAlmostEqual(b.low, 4 * a.low, places=11)
        self.assertEqual(a, c)
        self.assertAlmostEqual(b.estimate, 4 * a.estimate, places=11)
        swapped = x.reshape(-1, 2)[:, ::-1].ravel()
        self.assertAlmostEqual(
            bounded_kurtosis_interval(swapped.tolist()).estimate, a.estimate
        )

    def test_uninformative_and_finite_upper(self):
        a = bounded_kurtosis_interval([-1, 1])
        b = bounded_kurtosis_interval([-1, 1] * 128)
        assert a is not None and b is not None
        self.assertGreater(a.radius, 1)
        self.assertEqual(a.high, 16)
        self.assertLess(b.radius, 1)
        self.assertLess(b.high, 16)

    def test_zero_and_abstain(self):
        a = bounded_kurtosis_interval([0] * 256)
        assert a is not None
        self.assertEqual((a.low, a.high), (0, 0))
        self.assertIsNone(bounded_kurtosis_interval([-1e4, 1e4]))

    def test_invalid(self):
        for x in [[], [1], [1, float("nan")], [1e308, -1e308]]:
            with self.assertRaises(ValueError):
                bounded_kurtosis_interval(x)
        for k, c in [(0, 0.9), (101, 0.9), (float("nan"), 0.9), (9, 0.4), (9, 1)]:
            with self.assertRaises(ValueError):
                bounded_kurtosis_interval([0, 1], k, c)
