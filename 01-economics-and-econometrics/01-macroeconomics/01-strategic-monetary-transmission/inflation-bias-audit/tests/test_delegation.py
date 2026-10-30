import unittest
import math
from src.delegation import optimal_weight, oracle_weight, social_loss, state_average


class DelegationTest(unittest.TestCase):
    def test_state_formula_and_oracle_grid(self):
        for a in [0.5, 1.0, 2.0]:
            for w in [0.0, 0.5, 1.0, 2.0]:
                for k in [0.0, 0.5, 1.0]:
                    for s in [0.0, 0.5, 1.0, 3.0]:
                        q = optimal_weight(a, w, k, s)
                        self.assertTrue(0 <= q <= w)
                        self.assertAlmostEqual(
                            social_loss(q, a, w, k, s),
                            state_average(q, a, w, k, s),
                            places=11,
                        )
                        self.assertLessEqual(
                            social_loss(q, a, w, k, s),
                            social_loss(w, a, w, k, s) + 1e-11,
                        )
                        o = oracle_weight(a, w, k, s)
                        self.assertAlmostEqual(
                            social_loss(q, a, w, k, s),
                            social_loss(o, a, w, k, s),
                            places=10,
                        )

    def test_negative_controls(self):
        self.assertEqual(optimal_weight(1, 1, 0, 1), 1)
        self.assertEqual(optimal_weight(1, 1, 1, 0), 0)
        self.assertEqual(optimal_weight(1, 1, 0, 0), 1)
        self.assertGreater(social_loss(0, 1, 1, 0, 1), social_loss(1, 1, 1, 0, 1))

    def test_invalid(self):
        for s in [-1, 5, math.nan, math.inf]:
            with self.assertRaises(ValueError):
                optimal_weight(1, 1, 1, s)
        for q in [-1, 4, math.nan]:
            with self.assertRaises(ValueError):
                social_loss(q, 1, 1, 1, 1)
