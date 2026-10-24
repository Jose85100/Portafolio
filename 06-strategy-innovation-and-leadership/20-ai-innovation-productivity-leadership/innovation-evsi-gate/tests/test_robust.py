import unittest
from src.evsi import Case, evaluate
from src.robust import policy_value, select


class RobustTests(unittest.TestCase):
    def test_single_prior_reduces_to_original(self):
        c = Case()
        for n in (0, 10, 50, 100):
            self.assertAlmostEqual(policy_value(c, n, (6, 4)),
                                   float(evaluate(c, n)['net_value']), places=8)

    def test_delay_and_no_study(self):
        c = Case()
        self.assertEqual(policy_value(c, 0, (6, 4), 100), 0)
        self.assertLess(policy_value(c, 50, (6, 4), 1), policy_value(c, 50, (6, 4)))
        decision = select(c, [0, 50, 100], ((6, 4),), daily_discount=100)
        self.assertEqual(decision['selected']['n'], 0)

    def test_common_policy_can_lose(self):
        c = Case(alpha=1, beta=9)
        # Optimistic policy scales with no data; under pessimistic prior loses.
        self.assertLess(policy_value(c, 0, (9, 1)), 0)
        self.assertEqual(policy_value(c, 0, (9, 1), robust_terminal=((9, 1), (1, 9))), 0)

    def test_robust_no_worse_than_stopping(self):
        for rate in (0, .01, 1):
            result = select(Case(), [0, 10, 50], ((6, 4), (4, 6)), rate)
            self.assertGreaterEqual(result['selected']['worst_value'], -1e-8)

    def test_invalid(self):
        for rate, speed in ((-1, 10), (float('nan'), 10), (0, 0)):
            with self.assertRaises(ValueError):
                policy_value(Case(), 10, (6, 4), rate, speed)
        for sizes, priors in (([10], ((6, 4),)), ([0], ())):
            with self.assertRaises(ValueError):
                select(Case(), sizes, priors)
        with self.assertRaises(ValueError):
            policy_value(Case(), 10, (-1, 4))
