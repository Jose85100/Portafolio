import unittest
import numpy as np
from scipy.optimize import minimize_scalar
from src.ambiguity import robust_weight, regret, worst_regret
from src.delegation import optimal_weight


class AmbiguityTests(unittest.TestCase):
    def test_known_variance(self):
        for v in [0, 0.25, 1, 16]:
            self.assertAlmostEqual(
                robust_weight(1, 1, 1, v, v), optimal_weight(1, 1, 1, v**0.5), places=12
            )

    def test_degeneracies(self):
        self.assertEqual(robust_weight(1, 1, 0, 0, 4), 1)
        self.assertEqual(robust_weight(1, 0, 1, 0, 4), 0)

    def test_oracle_and_interior_envelope(self):
        for a in [0.5, 1, 2]:
            for k in [0.25, 1, 2]:
                for low, high in [(0, 1), (0.01, 4), (1, 16)]:
                    q = robust_weight(a, 1, k, low, high)
                    w = worst_regret(q, a, 1, k, low, high)
                    oracle = minimize_scalar(
                        lambda z: worst_regret(z, a, 1, k, low, high),
                        bounds=(0, 1),
                        method="bounded",
                        options={"xatol": 1e-13},
                    )
                    self.assertLessEqual(abs(w - oracle.fun), 1e-8)
                    self.assertAlmostEqual(
                        regret(q, a, 1, k, low), regret(q, a, 1, k, high), places=10
                    )
                    for v in np.linspace(low, high, 31):
                        self.assertLessEqual(regret(q, a, 1, k, float(v)), w + 1e-11)

    def test_negative_price_of_robustness(self):
        q = robust_weight(1, 1, 1, 0.04, 4)
        self.assertGreater(regret(q, 1, 1, 1, 0.04), 0)

    def test_invalid(self):
        for low, high in [(-1, 1), (2, 1), (0, 17), (float("nan"), 1)]:
            with self.assertRaises(ValueError):
                robust_weight(1, 1, 1, low, high)
