import unittest
import numpy as np
from src.monetary import policies, loss, oracle, best_response


class MonetaryTests(unittest.TestCase):
    def test_anchor(self):
        results = {name: [] for name in policies(1, 1, 1, 1)}
        for shock in [-1, 1]:
            for name, (pi, e) in policies(shock, 1, 1, 1).items():
                results[name].append((pi, e, loss(pi, e, shock, 1, 1, 1)))
        self.assertAlmostEqual(np.mean([v[2] for v in results["commitment"]]), 0.75)
        self.assertAlmostEqual(np.mean([v[2] for v in results["discretion"]]), 1.25)
        self.assertAlmostEqual(
            np.mean([v[2] for v in results["naive_fixed_expectations"]]), 0.5
        )
        self.assertAlmostEqual(
            np.mean([v[0] for v in results["naive_fixed_expectations"]]), 0.5
        )

    def test_exact_identity_and_oracle_properties(self):
        rng = np.random.default_rng(20261029)
        for _ in range(20):
            alpha, weight, target = (
                rng.uniform(0.1, 2),
                rng.uniform(0, 2),
                rng.uniform(0, 2),
            )
            sigma = rng.uniform(0, 2)
            disc = []
            commit = []
            for shock in [-sigma, sigma]:
                p = policies(shock, alpha, weight, target)
                for name, acc in [("commitment", commit), ("discretion", disc)]:
                    pi, e = p[name]
                    acc.append(loss(pi, e, shock, alpha, weight, target))
                pi, e = p["discretion"]
                self.assertAlmostEqual(
                    pi, oracle(e, shock, alpha, weight, target), delta=1e-6
                )
            self.assertAlmostEqual(
                np.mean(disc) - np.mean(commit),
                0.5 * (weight * alpha * target) ** 2,
                places=10,
            )

    def test_zero_target_control(self):
        for shock in [-2, 0, 2]:
            p = policies(shock, 1, 1, 0)
            self.assertEqual(p["commitment"], p["discretion"])

    def test_contracts(self):
        with self.assertRaises(ValueError):
            policies(0, 0, 1, 1)
        with self.assertRaises(ValueError):
            policies(0, 1, -1, 1)
        with self.assertRaises(ValueError):
            policies(float("nan"), 1, 1, 1)
        with self.assertRaises(ValueError):
            best_response(float("nan"), 0, 1, 1, 1)
        with self.assertRaises(ValueError):
            loss(float("nan"), 0, 0, 1, 1, 1)


if __name__ == "__main__":
    unittest.main()
