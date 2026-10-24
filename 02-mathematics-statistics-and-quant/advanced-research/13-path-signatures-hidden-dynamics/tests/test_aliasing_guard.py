import unittest

import numpy as np

from src.aliasing_guard import certify_area, plateau_stop, refine_sign


def loop(times, turns=1, orientation=1):
    theta = orientation * 2 * np.pi * turns * times
    return np.column_stack([np.cos(theta), np.sin(theta)])


class GuardTests(unittest.TestCase):
    def test_enclosure_circle_irregular_and_reversed(self):
        rng = np.random.default_rng(992)
        for turns in [1, 2, 4, 7]:
            for orientation in [-1, 1]:
                times = np.r_[0, np.sort(rng.uniform(size=60)), 1]
                c = certify_area(
                    loop(times, turns, orientation), times, 2 * np.pi * turns
                )
                self.assertLessEqual(
                    abs(c.area - orientation * turns * np.pi), c.radius
                )
                if c.sign:
                    self.assertEqual(c.sign, orientation)

    def test_refinement_and_false_plateau(self):
        def curve(t):
            return loop(t, 4)

        naive = plateau_stop(curve)
        c = refine_sign(curve, 8 * np.pi)
        self.assertLess(abs(naive.area), 1e-10)
        self.assertEqual(c.sign, 1)
        self.assertLess(c.segments, 4096)

    def test_insufficient_budget_abstains(self):
        c = refine_sign(lambda t: loop(t, 4), 8 * np.pi, max_segments=8)
        self.assertEqual(c.sign, 0)

    def test_constant_and_bad_inputs(self):
        t = np.array([0.0, 1.0])
        x = np.zeros((2, 2))
        self.assertEqual(certify_area(x, t, 0).sign, 0)
        for times, speed in [(np.array([0.0, 0.0]), 1), (t, -1), (t, np.nan)]:
            with self.assertRaises(ValueError):
                certify_area(x, times, speed)
        with self.assertRaises(ValueError):
            certify_area(np.ones((2, 3)), t, 1)
        with self.assertRaises(ValueError):
            certify_area(np.array([[0.0, 0.0], [2.0, 0.0]]), t, 1)
        with self.assertRaises(ValueError):
            refine_sign(lambda t: loop(t), 7, 8, 4)
        with self.assertRaises(ValueError):
            plateau_stop(lambda t: loop(t), -1)

    def test_false_assumption_not_inferred_from_samples(self):
        # Samples of seven forward turns look like one backward turn.
        t = np.linspace(0, 1, 9)
        c = certify_area(loop(t, 7), t, 6.2)
        self.assertEqual(c.sign, -1)
        self.assertLess(c.area + c.radius, 0)
        self.assertGreater(7 * np.pi, 0)
