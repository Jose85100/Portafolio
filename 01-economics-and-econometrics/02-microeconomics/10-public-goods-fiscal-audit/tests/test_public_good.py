import unittest
import numpy as np
from src.public_good import optimal, naive, no_policy, policy_welfare, oracle


class PublicGoodTests(unittest.TestCase):
    def test_anchor_and_budget(self):
        g = optimal(1, 2, 0.5)
        w, s, b = policy_welfare(g, 1, 2, 0.5)
        self.assertAlmostEqual(g, 1.2909944487358058, places=11)
        self.assertAlmostEqual(2 / (1 - s) - 1, g, places=12)
        self.assertAlmostEqual(b, s * g, places=12)
        self.assertGreater(w, policy_welfare(1, 1, 2, 0.5)[0])
        self.assertLess(
            policy_welfare(2, 1, 2, 0.5)[0], policy_welfare(1, 1, 2, 0.5)[0]
        )

    def test_zero_cost_and_no_subsidy_corner(self):
        self.assertAlmostEqual(optimal(1, 2, 0), naive(1, 2))
        self.assertEqual(optimal(1, 2, 2), no_policy(2))
        self.assertEqual(policy_welfare(1, 1, 2, 2)[2], 0)

    def test_oracle_and_dominance_properties(self):
        rng = np.random.default_rng(20261028)
        for _ in range(20):
            high = rng.uniform(1.2, 4)
            low = rng.uniform(0.2, high - 0.1)
            tax = rng.uniform(0, 3)
            g = optimal(low, high, tax)
            w = policy_welfare(g, low, high, tax)[0]
            _, numeric = oracle(low, high, tax)
            self.assertAlmostEqual(w, numeric, places=8)
            self.assertGreaterEqual(
                w + 1e-10, policy_welfare(no_policy(high), low, high, tax)[0]
            )
            self.assertGreaterEqual(
                w + 1e-10, policy_welfare(naive(low, high), low, high, tax)[0]
            )

    def test_transfer_is_not_resource_gain(self):
        g = 2
        w, s, b = policy_welfare(g, 1, 2, 0)
        naive_before_tax = 3 * np.log1p(g) - (1 - s) * g
        self.assertAlmostEqual(naive_before_tax - w, b)

    def test_contracts(self):
        for low, high, tax in [
            (0, 2, 0),
            (2, 1, 0),
            (1, 2, -1),
            (1, 21, 0),
            (float("nan"), 2, 0),
        ]:
            with self.assertRaises(ValueError):
                optimal(low, high, tax)
        with self.assertRaises(ValueError):
            no_policy(1)
        with self.assertRaises(ValueError):
            policy_welfare(0, 1, 2, 0)


if __name__ == "__main__":
    unittest.main()
