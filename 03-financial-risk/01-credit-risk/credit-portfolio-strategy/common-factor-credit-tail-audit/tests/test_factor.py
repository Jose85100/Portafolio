import math
import unittest

from src.base import independent_pmf, tail
from src.factor import common_factor_pmf, stability_passed


class TestFactor(unittest.TestCase):
    def test_independence_identity(self):
        self.assertEqual(
            common_factor_pmf([1, 5, 9], [0.01, 0.2, 1.0], 0),
            independent_pmf([1, 5, 9], [0.01, 0.2, 1.0]),
        )

    def test_bivariate_orthant_oracle(self):
        rho = 0.5
        both = 0.25 + math.asin(rho) / (2 * math.pi)
        expected = [both, 1 - 2 * both, both]
        actual = common_factor_pmf([1, 1], [0.5, 0.5], rho, 64)
        for a, b in zip(actual, expected):
            self.assertAlmostEqual(a, b, places=12)

    def test_single_name_and_endpoints(self):
        actual = common_factor_pmf([5], [0.02], 0.2, 64)
        self.assertAlmostEqual(actual[0], 0.98, places=12)
        self.assertAlmostEqual(actual[5], 0.02, places=12)
        fixed = common_factor_pmf([2, 3], [0.0, 1.0], 0.7, 64)
        self.assertAlmostEqual(fixed[3], 1, places=12)

    def test_mass_mean_and_permutation(self):
        weights = [2, 5, 9]
        ps = [0.01, 0.03, 0.1]
        pmf = common_factor_pmf(weights, ps, 0.2, 64)
        self.assertAlmostEqual(math.fsum(pmf), 1, places=12)
        self.assertAlmostEqual(
            math.fsum(i * p for i, p in enumerate(pmf)),
            sum(w * p for w, p in zip(weights, ps)),
            places=10,
        )
        reverse = common_factor_pmf(weights[::-1], ps[::-1], 0.2, 64)
        for a, b in zip(pmf, reverse):
            self.assertAlmostEqual(a, b, places=14)
        self.assertGreaterEqual(tail(pmf, 0.99).es, tail(pmf, 0.99).var)

    def test_stability_and_validation(self):
        self.assertTrue(stability_passed([0.5, 0.5], [0.5, 0.5]))
        self.assertFalse(stability_passed([0.5, 0.5], [0.4, 0.6]))
        with self.assertRaises(ValueError):
            stability_passed([1.0], [0.5, 0.5])
        with self.assertRaises(ValueError):
            stability_passed([1.0], [1.0], es_tolerance=-1)
        for rho in [-1, 1, math.nan]:
            with self.assertRaises(ValueError):
                common_factor_pmf([1], [0.1], rho)
        for nodes in [1, True, 1.5, 1025]:
            with self.assertRaises(ValueError):
                common_factor_pmf([1], [0.1], 0.1, nodes)
