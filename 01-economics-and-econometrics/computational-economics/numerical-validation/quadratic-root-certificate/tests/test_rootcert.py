import sys
from fractions import Fraction as F
from pathlib import Path
import unittest

from hypothesis import given, settings, strategies as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rootcert import (  # noqa: E402
    Interval,
    evaluate,
    isolate_quadratic,
    select_in_domain,
    verify_certificate,
)


class RootCertificateTests(unittest.TestCase):
    def test_fire_sale_roots(self) -> None:
        roots = isolate_quadratic(F(1), F(-1), F(4, 25), decimal_digits=20)
        self.assertTrue(verify_certificate(F(1), F(-1), F(4, 25), roots))
        self.assertEqual([float(r.midpoint) for r in roots], [0.2, 0.8])

    def test_double_root_is_exact(self) -> None:
        roots = isolate_quadratic(F(1), F(-1), F(1, 4))
        self.assertEqual((roots[0].lower, roots[0].multiplicity), (F(1, 2), 2))
        self.assertTrue(verify_certificate(F(1), F(-1), F(1, 4), roots))

    def test_no_real_roots(self) -> None:
        roots = isolate_quadratic(F(1), F(0), F(1))
        self.assertEqual(roots, ())
        self.assertTrue(verify_certificate(F(1), F(0), F(1), roots))

    def test_negative_leading_coefficient(self) -> None:
        roots = isolate_quadratic(F(-1), F(1), F(-4, 25))
        self.assertTrue(verify_certificate(F(-1), F(1), F(-4, 25), roots))

    def test_regime_filter_does_not_prove_admissibility(self) -> None:
        roots = isolate_quadratic(F(1), F(-23, 25), F(14, 125))
        selected = select_in_domain(roots, F(1, 20), F(1, 5))
        self.assertEqual(len(selected), 1)

    def test_validation_errors(self) -> None:
        with self.assertRaises(ValueError):
            isolate_quadratic(F(0), F(1), F(1))
        with self.assertRaises(ValueError):
            isolate_quadratic(F(1), F(0), F(-1), decimal_digits=0)
        with self.assertRaises(ValueError):
            select_in_domain((), F(1), F(0))

    def test_rejects_corrupt_certificates(self) -> None:
        self.assertFalse(verify_certificate(F(1), F(0), F(-1), ()))
        overlapping = (Interval(F(-1), F(1), 1), Interval(F(0), F(2), 1))
        self.assertFalse(verify_certificate(F(1), F(0), F(-1), overlapping))
        wrong_multiplicity = (Interval(F(-2), F(-1), 2), Interval(F(1), F(2), 1))
        self.assertFalse(verify_certificate(F(1), F(0), F(-1), wrong_multiplicity))
        wrong_sign = (Interval(F(-3), F(-2), 1), Interval(F(1), F(2), 1))
        self.assertFalse(verify_certificate(F(1), F(0), F(-1), wrong_sign))
        self.assertEqual(Interval(F(1), F(3), 1).width, F(2))

    @settings(max_examples=80, deadline=None)
    @given(
        r1=st.integers(-100, 99),
        gap=st.integers(1, 100),
        scale=st.integers(1, 30),
    )
    def test_rational_roots_are_enclosed(self, r1: int, gap: int, scale: int) -> None:
        x1, x2 = F(r1, scale), F(r1 + gap, scale)
        b, c = -(x1 + x2), x1 * x2
        roots = isolate_quadratic(F(1), b, c, decimal_digits=24)
        self.assertTrue(verify_certificate(F(1), b, c, roots))
        self.assertTrue(roots[0].lower <= x1 <= roots[0].upper)
        self.assertTrue(roots[1].lower <= x2 <= roots[1].upper)

    @settings(max_examples=40, deadline=None)
    @given(k=st.integers(-1000, 1000), scale=st.integers(1, 100))
    def test_exact_double_roots(self, k: int, scale: int) -> None:
        root = F(k, scale)
        intervals = isolate_quadratic(F(1), -2 * root, root * root)
        self.assertEqual(intervals[0].lower, root)
        self.assertEqual(evaluate(F(1), -2 * root, root * root, root), 0)


if __name__ == "__main__":
    unittest.main()
