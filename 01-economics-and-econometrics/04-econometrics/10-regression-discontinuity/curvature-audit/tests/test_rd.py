import unittest
import numpy as np
from src.rd import estimate, sample


class RDTests(unittest.TestCase):
    def test_exact_linear_jump(self):
        x = np.linspace(-1, 1, 1000)
        y = 2 + 0.3 * x + (x >= 0) * (1 + 0.4 * x)
        for h in [1, 0.5, 0.1]:
            self.assertAlmostEqual(estimate(x, y, h)[0], 1, places=12)

    def test_matrix_oracle(self):
        x, y = sample(2, 500)
        m = np.abs(x) <= 0.4
        t = (x[m] >= 0).astype(float)
        X = np.column_stack([np.ones(m.sum()), x[m], t, t * x[m]])
        beta = np.linalg.lstsq(X, y[m], rcond=None)[0]
        self.assertAlmostEqual(estimate(x, y, 0.4)[0], beta[2], places=12)

    def test_invariance(self):
        for seed in range(25):
            x, y = sample(seed, 1000)
            a = estimate(x, y, 0.3)[0]
            self.assertAlmostEqual(
                a, estimate(x * 3 + 7, y + 14, 0.9, cutoff=7)[0], places=11
            )
            order = np.arange(len(x))[::-1]
            self.assertAlmostEqual(a, estimate(x[order], y[order], 0.3)[0], places=12)

    def test_population_curvature_bias(self):
        x = np.linspace(-1, 1, 100000)
        t = x >= 0
        y = t + 0.4 * x + 3 * x * x + 4 * t * x * x
        self.assertAlmostEqual(estimate(x, y, 1)[0], 1 - 4 / 6, delta=0.0001)
        self.assertAlmostEqual(estimate(x, y, 0.2)[0], 1 - 4 * 0.2**2 / 6, delta=0.0001)

    def test_latent_jump_not_cured(self):
        x, y = sample(2, 10000, latent_jump=0.6, noise_sd=0)
        self.assertGreater(estimate(x, y, 0.1)[0], 1.5)

    def test_contracts(self):
        a = np.arange(20, dtype=float)
        for x, y, h in [
            (a, a, -1),
            (a, a, float("nan")),
            (a[:-1], a, 1),
            (a[:, None], a, 1),
            (a * float("nan"), a, 1),
            (a, a, 0.1),
        ]:
            with self.assertRaises(ValueError):
                estimate(x, y, h)
        with self.assertRaises(ValueError):
            estimate(np.r_[-np.ones(10), np.ones(10)], a, 2)
        with self.assertRaises(ValueError):
            estimate(a, a, 1, min_side=1)
        with self.assertRaises(ValueError):
            sample(0, 3)
        with self.assertRaises(ValueError):
            sample(0, 100, noise_sd=-1)

    def test_seed(self):
        for a, b in zip(sample(2, 100), sample(2, 100)):
            np.testing.assert_array_equal(a, b)


if __name__ == "__main__":
    unittest.main()
