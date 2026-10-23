import unittest
import numpy as np
from src.conformal import thresholds, ratios


class ConformalTests(unittest.TestCase):
    def test_equal_weights_finite_sample_rank(self):
        q = thresholds(np.arange(1.0, 10.0), np.ones(9), np.ones(1), 0.1)
        self.assertEqual(q[0], 9.0)

    def test_infinity_is_not_clipped(self):
        self.assertTrue(
            np.isinf(
                thresholds(np.array([1.0, 2.0]), np.ones(2), np.array([10.0]), 0.1)[0]
            )
        )

    def test_naive_is_ablation(self):
        self.assertEqual(
            thresholds(np.array([1.0, 2.0]), np.ones(2), np.array([10.0]), 0.1, False)[
                0
            ],
            2.0,
        )

    def test_scaling_and_permutation_property(self):
        rng = np.random.default_rng(42)
        for _ in range(100):
            s = rng.random(20)
            w = rng.uniform(0.1, 4, 20)
            t = rng.uniform(0.1, 4, 8)
            base = thresholds(s, w, t)
            order = rng.permutation(20)
            np.testing.assert_array_equal(
                base, thresholds(s[order], w[order] * 1e100, t * 1e100)
            )

    def test_alpha_monotonic_property(self):
        rng = np.random.default_rng(18)
        for _ in range(100):
            s = rng.random(20)
            w = rng.uniform(0.1, 4, 20)
            t = rng.uniform(0.1, 4, 8)
            self.assertTrue(
                np.all(thresholds(s, w, t, 0.05) >= thresholds(s, w, t, 0.2))
            )

    def test_test_mass_monotonic(self):
        s = np.arange(10.0)
        w = np.ones(10)
        q = thresholds(s, w, np.array([0.1, 1.0, 3.0, 9.0]))
        self.assertTrue(np.all(q[1:] >= q[:-1]))

    def test_invalid_inputs(self):
        for s, w, t, a in [
            ([], [], [1], 0.1),
            ([1], [1], [], 0.1),
            ([1], [1e-300], [1e300], 0.1),
            ([1], [0], [1], 0.1),
            ([1], [1], [float("nan")], 0.1),
            ([-1], [1], [1], 0.1),
            ([1], [1], [1], 1),
        ]:
            with self.assertRaises(ValueError):
                thresholds(np.array(s), np.array(w), np.array(t), a)

    def test_ratios(self):
        np.testing.assert_allclose(
            ratios(np.array([True, False]), 0.1, 0.8), [8.0, 2 / 9]
        )
        with self.assertRaises(ValueError):
            ratios(np.array([True]), 0, 0.8)

    def test_ties(self):
        np.testing.assert_array_equal(
            thresholds(np.ones(20), np.ones(20), np.ones(3)), np.ones(3)
        )


if __name__ == "__main__":
    unittest.main()
