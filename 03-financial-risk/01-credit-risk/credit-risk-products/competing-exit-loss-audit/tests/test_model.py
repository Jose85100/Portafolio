import math
import unittest
from fractions import Fraction
from src.model import project


class TestProjection(unittest.TestCase):
    def test_rational_oracle(self):
        d, p, e, lgd, r = (
            Fraction(1, 50),
            Fraction(1, 10),
            Fraction(100),
            Fraction(9, 20),
            Fraction(1, 200),
        )
        active = Fraction(1)
        loss = Fraction(0)
        pd = Fraction(0)
        for t in range(1, 13):
            pd += active * d
            loss += active * d * e * lgd / (1 + r) ** t
            active *= 1 - d - p
        result = project(
            [float(d)] * 12, [float(p)] * 12, [100.0] * 12, float(lgd), float(r)
        )
        self.assertAlmostEqual(result.default_probability, float(pd), places=14)
        self.assertAlmostEqual(result.expected_loss, float(loss), places=12)
        self.assertAlmostEqual(result.active_probability, float(active), places=14)

    def test_zero_competing_exit_and_one_period(self):
        result = project([0.02] * 12, [0.0] * 12, [100.0] * 12, 1, 0)
        self.assertAlmostEqual(result.default_probability, 1 - 0.98**12, places=14)
        a = project([0.02], [0.1], [100.0])
        b = project([0.02], [0.0], [100.0])
        self.assertEqual(a.expected_loss, b.expected_loss)

    def test_mass_absorbing_and_zero_exposure(self):
        all_prepay = project([0.0, 0.9], [1.0, 0.0], [100.0, 100.0])
        self.assertEqual(all_prepay.prepayment_probability, 1)
        self.assertEqual(all_prepay.default_probability, 0)
        self.assertEqual(project([1.0], [0.0], [0.0]).expected_loss, 0)
        result = project([0.1] * 12, [0.2] * 12, [100.0] * 12)
        self.assertAlmostEqual(
            result.default_probability
            + result.prepayment_probability
            + result.active_probability,
            1,
            places=14,
        )
        self.assertLess(result.maximum_mass_error, 1e-12)

    def test_monotone_prepay_discount_and_scaling(self):
        a = project([0.02] * 12, [0.01] * 12, [100.0] * 12, rate=0)
        b = project([0.02] * 12, [0.1] * 12, [100.0] * 12, rate=0)
        self.assertGreater(a.expected_loss, b.expected_loss)
        self.assertGreater(
            b.expected_loss,
            project([0.02] * 12, [0.1] * 12, [100.0] * 12, rate=0.01).expected_loss,
        )
        self.assertAlmostEqual(
            project([0.02] * 12, [0.1] * 12, [200.0] * 12, rate=0).expected_loss,
            2 * b.expected_loss,
            places=12,
        )

    def test_invalid(self):
        for args in [
            ([], [], []),
            ([0.2], [0.9], [100.0]),
            ([math.nan], [0.0], [100.0]),
            ([0.1], [0.0], [-1.0]),
            ([0.1], [0.0], [math.inf]),
            ([0.1], [0.0, 0.0], [100.0]),
        ]:
            with self.assertRaises(ValueError):
                project(*args)
        for lgd, r in [(math.nan, 0), (-1, 0), (0.5, -0.1), (0.5, math.inf)]:
            with self.assertRaises(ValueError):
                project([0.1], [0.0], [100.0], lgd, r)
