import unittest

import numpy as np

from src.moments import correct_covariance, estimate, generate, population_covariance


class MomentTests(unittest.TestCase):
    def test_population_oracles(self):
        for beta in [-1.0, 0.0, 0.3, 2.0]:
            cov = population_covariance(beta)
            self.assertAlmostEqual(correct_covariance(cov, 1).slope, beta, places=12)
            self.assertAlmostEqual(
                correct_covariance(cov, 0).slope, beta + 0.32 / 0.57, places=12
            )
            self.assertEqual(
                correct_covariance(cov, 1.5).status, "nonpositive_moment_matrix"
            )

    def test_zero_noise_matches_ols(self):
        x, w, y, _ = generate(100, 0.3, 9)
        oracle = np.linalg.lstsq(
            np.column_stack([np.ones(len(x)), x, w]), y, rcond=None
        )[0][1]
        self.assertAlmostEqual(estimate(x, w, y, 0).slope, float(oracle), places=12)

    def test_units_translation_and_target_linearity_randomized(self):
        for seed in range(10):
            x, w, y, _ = generate(1000, 0.3, seed)
            a = estimate(x, w, y, 1)
            b = estimate(4 * x + 3, 2 * w - 7, 3 * y + 8, 4)
            self.assertEqual(a.status, b.status)
            if a.slope is not None:
                self.assertAlmostEqual(b.slope, 3 * a.slope / 4, places=10)
                self.assertAlmostEqual(
                    estimate(x, w, y + 2 * x, 1).slope, a.slope + 2, places=10
                )

    def test_bad_inputs_and_abstentions(self):
        self.assertEqual(
            correct_covariance(population_covariance(0), 3).status,
            "nonpositive_signal_variance",
        )
        self.assertEqual(
            correct_covariance(population_covariance(0), 1, max_condition=2).status,
            "ill_conditioned",
        )
        for cov, var in [
            (np.ones((2, 2)), 0),
            (np.full((3, 3), np.nan), 0),
            (np.array([[1.0, 2, 3], [0, 1, 2], [3, 2, 1]]), 0),
            (np.eye(3), -1),
        ]:
            with self.assertRaises(ValueError):
                correct_covariance(cov, var)
        with self.assertRaises(ValueError):
            correct_covariance(np.eye(3), 0, max_condition=1)
        with self.assertRaises(ValueError):
            estimate(np.zeros(3), np.zeros(3), np.zeros(3), 0)
        with self.assertRaises(ValueError):
            estimate(np.zeros(4), np.zeros(5), np.zeros(4), 0)
        with self.assertRaises(ValueError):
            estimate(np.zeros(4), np.zeros(4), np.full(4, np.nan), 0)
        with self.assertRaises(ValueError):
            generate(1, 0, 1)
