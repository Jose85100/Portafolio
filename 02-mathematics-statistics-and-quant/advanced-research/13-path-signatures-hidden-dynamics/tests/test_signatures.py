import unittest
import numpy as np
from src.signatures import signature, compose, signed_area, polygon_area, circle


class SignatureTests(unittest.TestCase):
    def test_square_oracle(self):
        x = np.array([[0.0, 0.0], [1, 0], [1, 1], [0, 1], [0, 0]])
        self.assertAlmostEqual(signed_area(x), 1.0)
        self.assertAlmostEqual(polygon_area(x), 1.0)

    def test_chen_shuffle_translation_reversal_randomized(self):
        rng = np.random.default_rng(422)
        for n in (2, 3, 9, 32):
            for d in (1, 2, 4):
                x = rng.normal(size=(n, d)).cumsum(axis=0)
                a, b = signature(x)
                m = n // 2
                c, e = compose(signature(x[: m + 1]), signature(x[m:]))
                np.testing.assert_allclose(a, c, atol=1e-12)
                np.testing.assert_allclose(b, e, atol=1e-12)
                np.testing.assert_allclose(b + b.T, np.outer(a, a), atol=1e-12)
                ar, br = signature(x[::-1])
                np.testing.assert_allclose(ar, -a, atol=1e-12)
                np.testing.assert_allclose(br, np.outer(a, a) - b, atol=1e-12)
                at, bt = signature(x + 30)
                np.testing.assert_allclose(bt, b, atol=1e-11)
                if d == 2:
                    self.assertAlmostEqual(signed_area(x), polygon_area(x), places=10)

    def test_collinear_subdivision_and_stationary_points(self):
        x = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]])
        refined = np.array(
            [[0.0, 0.0], [0.1, 0.0], [0.1, 0.0], [1.0, 0.0], [1.0, 0.8], [1.0, 1.0]]
        )
        for left, right in zip(signature(x), signature(refined)):
            np.testing.assert_allclose(left, right, atol=1e-12)

    def test_tree_like(self):
        a, b = signature(np.array([[0.0, 0.0], [1, 2], [0, 0]]))
        np.testing.assert_allclose(a, 0)
        np.testing.assert_allclose(b, 0)

    def test_single_point(self):
        a, b = signature(np.zeros((1, 2)))
        self.assertEqual(float(b.sum() + a.sum()), 0)

    def test_bad_inputs(self):
        for x in (
            np.array([]),
            np.zeros((0, 2)),
            np.zeros((1, 0)),
            np.array([[np.nan, 0]]),
        ):
            with self.assertRaises(ValueError):
                signature(x)
        with self.assertRaises(ValueError):
            signed_area(np.zeros((2, 3)))
        with self.assertRaises(ValueError):
            circle(0)
        with self.assertRaises(ValueError):
            polygon_area(np.zeros((2, 3)))
        with self.assertRaises(ValueError):
            compose(signature(np.zeros((1, 2))), signature(np.zeros((1, 3))))

    def test_aliasing(self):
        self.assertLess(abs(signed_area(circle(4, turns=2))), 1e-12)
        self.assertGreater(signed_area(circle(256, turns=2)), 6)
