import math
import unittest

from src.calendar import project_calendar


class CalendarTests(unittest.TestCase):
    def test_closed_form(self):
        r = project_calendar([1.0], [0.24], [1.2], [100.0])
        self.assertAlmostEqual(
            r.exact_loss, 100 * 0.45 * 0.24 / 1.5 * (-math.expm1(-1.5)), places=13
        )
        self.assertAlmostEqual(
            r.default_probability, 0.24 / 1.44 * (-math.expm1(-1.44)), places=14
        )

    def test_partition_and_mass(self):
        one = project_calendar([1.0], [0.24], [1.2], [100.0])
        for n in (2, 12, 100, 360):
            r = project_calendar([1 / n] * n, [0.24] * n, [1.2] * n, [100.0] * n)
            self.assertAlmostEqual(r.exact_loss, one.exact_loss, places=12)
            self.assertAlmostEqual(
                r.default_probability + r.prepayment_probability + r.survival,
                1,
                places=12,
            )
            self.assertLessEqual(r.endpoint_loss, r.exact_loss + 1e-12)

    def test_negative_zero_discount(self):
        r = project_calendar(
            [0.1, 0.9], [0.2, 0.4], [1.0, 0.0], [100.0, 80.0], discount_force=0.0
        )
        self.assertAlmostEqual(r.exact_loss, r.endpoint_loss, places=13)
        z = project_calendar([1.0], [0.0], [0.0], [100.0])
        self.assertEqual(z.exact_loss, 0.0)
        self.assertEqual(z.survival, 1.0)

    def test_refinement(self):
        errors = []
        for n in (1, 2, 12, 100):
            r = project_calendar([1 / n] * n, [0.24] * n, [1.2] * n, [100.0] * n)
            errors.append(r.exact_loss - r.endpoint_loss)
        self.assertEqual(errors, sorted(errors, reverse=True))

    def test_invalid(self):
        for dt, d, p, e in (
            (0, 0.2, 1, 100),
            (1, -1, 0, 100),
            (1, 0.2, float("nan"), 100),
            (1, 0.2, 1, -1),
        ):
            with self.assertRaises(ValueError):
                project_calendar([dt], [d], [p], [e])
        with self.assertRaises(ValueError):
            project_calendar([1.0], [], [0.0], [100.0])
        with self.assertRaises(ValueError):
            project_calendar([1.0], [1.0], [0.0], [100.0], discount_force=-1.0)

    def test_invalid_bounds(self):
        for lgd in (-1.0, float("nan")):
            with self.assertRaises(ValueError):
                project_calendar([1.0], [0.1], [0.0], [100.0], lgd=lgd)
        with self.assertRaises(ValueError):
            project_calendar([1.0], [1e308], [1e308], [100.0])
