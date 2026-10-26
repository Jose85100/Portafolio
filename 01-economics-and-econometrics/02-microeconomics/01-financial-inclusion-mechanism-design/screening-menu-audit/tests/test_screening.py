import unittest
import numpy as np
from src.screening import (
    Economy,
    analytic,
    uniform,
    profit,
    slacks,
    strictify,
    qp,
    realized,
)


class ScreeningTests(unittest.TestCase):
    def test_anchor(self):
        e = Economy()
        a = analytic(e)
        np.testing.assert_allclose(a, [0.75, 2, 0.75, 3.25])
        self.assertAlmostEqual(profit(a, e), 0.625)
        self.assertAlmostEqual(uniform(e)[2], 0.5)
        self.assertAlmostEqual(realized(a, e, tie="smallest"), 0.09375)

    def test_grid_properties_and_qp(self):
        rng = np.random.default_rng(20261026)
        for _ in range(30):
            low = rng.uniform(0.5, 2)
            e = Economy(
                low,
                low + rng.uniform(0.2, 2),
                rng.uniform(0.05, 0.95),
                rng.uniform(0.5, 2),
            )
            a = analytic(e)
            num, _ = qp(e)
            self.assertGreaterEqual(slacks(a, e).min(), -1e-9)
            self.assertGreaterEqual(profit(a, e) + 1e-9, uniform(e)[2])
            self.assertAlmostEqual(profit(a, e), profit(num, e), places=7)

    def test_exclusion_region(self):
        e = Economy(p=0.7)
        self.assertEqual(analytic(e)[0], 0)
        self.assertAlmostEqual(profit(analytic(e), e), uniform(e)[2])

    def test_strict_implementation_and_misspecification(self):
        e = Economy()
        s = strictify(analytic(e), e)
        self.assertGreater(slacks(s, e).min(), 0)
        self.assertAlmostEqual(realized(s, e, tie="smallest"), profit(s, e))
        self.assertLess(realized(s, e, true_low=0.8), uniform(Economy(low=0.8))[2])

    def test_first_best_without_ic_fails(self):
        e = Economy()
        fb = np.array([1.0, 2.0, 1.0, 4.0])
        self.assertAlmostEqual(profit(fb, e), 0.8)
        self.assertLess(slacks(fb, e)[-1], 0)

    def test_failure_paths_and_invalid_preferences(self):
        from unittest.mock import patch
        from types import SimpleNamespace

        with patch(
            "src.screening.minimize",
            return_value=SimpleNamespace(
                success=False, x=np.zeros(4), message="forced"
            ),
        ):
            with self.assertRaises(RuntimeError):
                qp(Economy())
        with self.assertRaises(ValueError):
            realized(analytic(Economy()), Economy(), true_low=float("nan"))
        with self.assertRaises(ValueError):
            profit(np.full(4, float("nan")), Economy())
        with self.assertRaises(ValueError):
            strictify(np.array([0.75, 2, 0.75, 3.9]), Economy())

    def test_contracts(self):
        for args in [
            dict(low=0),
            dict(high=1),
            dict(p=0),
            dict(p=1),
            dict(cost=0),
            dict(low=float("nan")),
        ]:
            with self.assertRaises(ValueError):
                Economy(**args)
        with self.assertRaises(ValueError):
            profit(np.zeros(3), Economy())
        with self.assertRaises(ValueError):
            strictify(analytic(Economy()), Economy(), epsilon=1)
        with self.assertRaises(ValueError):
            strictify(analytic(Economy()), Economy(), epsilon=-1)
        with self.assertRaises(ValueError):
            realized(analytic(Economy()), Economy(), tie="bad")


if __name__ == "__main__":
    unittest.main()
