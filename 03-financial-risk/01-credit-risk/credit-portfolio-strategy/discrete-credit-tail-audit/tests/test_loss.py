import itertools
import math
import random
import unittest

from src.loss import independent_pmf, normal_tail, tail


class TestLoss(unittest.TestCase):
    def test_brute_force_oracle(self):
        rng = random.Random(20261025)
        for n in range(1, 8):
            weights = [rng.randrange(0, 5) for _ in range(n)]
            ps = [rng.choice([0.0, 0.1, 0.5, 1.0]) for _ in range(n)]
            expected = [0.0] * (sum(weights) + 1)
            for bits in itertools.product([0, 1], repeat=n):
                probability = math.prod(p if b else 1 - p for p, b in zip(ps, bits))
                expected[sum(w * b for w, b in zip(weights, bits))] += probability
            actual = independent_pmf(weights, ps)
            for a, b in zip(actual, expected):
                self.assertAlmostEqual(a, b, places=13)

    def test_mass_moments(self):
        weights = [1, 7, 11, 3]
        ps = [0.01, 0.1, 0.6, 0.9]
        pmf = independent_pmf(weights, ps)
        mean = sum(x * p for x, p in enumerate(pmf))
        variance = sum((x - mean) ** 2 * p for x, p in enumerate(pmf))
        self.assertAlmostEqual(sum(pmf), 1)
        self.assertAlmostEqual(mean, sum(w * p for w, p in zip(weights, ps)))
        self.assertAlmostEqual(
            variance, sum(w * w * p * (1 - p) for w, p in zip(weights, ps))
        )

    def test_partial_atom_and_deterministic(self):
        self.assertEqual(tail([0.8, 0.0, 0.2], 0.9).es, 2.0)
        self.assertAlmostEqual(tail([0.8, 0.0, 0.2], 0.5).es, 0.8)
        self.assertEqual(tail([1.0], 0.99).var, 0.0)
        self.assertEqual(tail(independent_pmf([2, 3], [1.0, 1.0])).es, 5.0)
        self.assertEqual(normal_tail([5], [1.0]).var, 5.0)

    def test_scale_permutation_and_zero(self):
        p = independent_pmf([2, 5], [0.2, 0.3])
        t = tail(p, 0.8)
        self.assertEqual(p, independent_pmf([5, 2], [0.3, 0.2]))
        self.assertEqual(p, independent_pmf([2, 5, 0], [0.2, 0.3, 0.7]))
        scaled = tail(independent_pmf([6, 15], [0.2, 0.3]), 0.8)
        self.assertAlmostEqual(scaled.var, 3 * t.var)
        self.assertAlmostEqual(scaled.es, 3 * t.es)

    def test_invalid(self):
        for weights, ps in [
            ([], []),
            ([1], []),
            ([-1], [0.2]),
            ([True], [0.2]),
            ([1.5], [0.2]),
            ([20001], [0.2]),
            ([1], [math.nan]),
            ([1], [1.2]),
        ]:
            with self.assertRaises(ValueError):
                independent_pmf(weights, ps)
        for pmf in ([], [-1, 2], [math.inf], [0.5]):
            with self.assertRaises(ValueError):
                tail(pmf)
        for alpha in (0, 1, math.nan):
            with self.assertRaises(ValueError):
                tail([1.0], alpha)
            with self.assertRaises(ValueError):
                normal_tail([1], [0.1], alpha)
