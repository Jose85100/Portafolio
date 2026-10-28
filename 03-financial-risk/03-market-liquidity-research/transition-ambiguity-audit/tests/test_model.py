import itertools
import math
import unittest

from src.baseline import nominal
from src.model import risk_band


class TestBand(unittest.TestCase):
    def test_singleton_matches_independent_forward_dp(self):
        for h, c, p in itertools.product(
            [0, 1, 4, 10], [0, 2, 6], [(0.05, 0.8), (0.8, 0.2), (0.0, 1.0)]
        ):
            result = risk_band(c, h, [[p[0], p[0]], [p[1], p[1]]])
            expected = nominal(c, h, p)
            self.assertAlmostEqual(result.lower, expected, places=13)
            self.assertAlmostEqual(result.upper, expected, places=13)

    def test_contains_static_grid_and_nested_sets(self):
        bounds = [[0.03, 0.07], [0.7, 0.9]]
        band = risk_band(3, 12, bounds)
        for q0, q1 in itertools.product([0.03, 0.05, 0.07], [0.7, 0.8, 0.9]):
            probability = nominal(3, 12, [q0, q1])
            self.assertLessEqual(band.lower, probability + 1e-12)
            self.assertGreaterEqual(band.upper + 1e-12, probability)
        wider = risk_band(3, 12, [[0, 0.2], [0.5, 1.0]])
        self.assertLessEqual(wider.lower, band.lower + 1e-12)
        self.assertGreaterEqual(wider.upper + 1e-12, band.upper)

    def test_analytical_two_day_and_boundary(self):
        # From cash0 and initial normal, day1+1 survives; day2 stress-2 breaches.
        band = risk_band(0, 2, [[0.1, 0.4], [0.2, 0.8]], [1.0, 0.0])
        self.assertEqual(band.lower, 0.1)
        self.assertEqual(band.upper, 0.4)
        self.assertEqual(risk_band(2, 1, [[0, 1], [0, 1]], [0, 1]).upper, 0)
        self.assertEqual(risk_band(1, 1, [[0, 1], [0, 1]], [0, 1]).lower, 1)

    def test_buffer_monotonicity_and_no_ambiguity_effect_at_h1(self):
        bands = [risk_band(c, 20, [[0.03, 0.07], [0.7, 0.9]]) for c in range(31)]
        self.assertEqual(
            [x.upper for x in bands], sorted([x.upper for x in bands], reverse=True)
        )
        self.assertEqual(
            risk_band(1, 1, [[0, 1], [0, 1]]).lower,
            risk_band(1, 1, [[0, 1], [0, 1]]).upper,
        )

    def test_invalid(self):
        for cash, h, bounds, initial in [
            (-1, 1, [[0, 1], [0, 1]], [0.8, 0.2]),
            (True, 1, [[0, 1], [0, 1]], [0.8, 0.2]),
            (0, 41, [[0, 1], [0, 1]], [0.8, 0.2]),
            (0, True, [[0, 1], [0, 1]], [0.8, 0.2]),
            (0, 1, [[0.8, 0.2], [0, 1]], [0.8, 0.2]),
            (0, 1, [[0, math.nan], [0, 1]], [0.8, 0.2]),
            (0, 1, [[0, 1]], [0.8, 0.2]),
            (0, 1, [[0, 1], [0, 1]], [0.8, 0.1]),
        ]:
            with self.assertRaises(ValueError):
                risk_band(cash, h, bounds, initial)
