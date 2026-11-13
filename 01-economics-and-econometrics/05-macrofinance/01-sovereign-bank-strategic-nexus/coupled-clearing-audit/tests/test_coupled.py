"""Analytical oracles, generated invariants and prior-model reductions."""

from dataclasses import replace
from fractions import Fraction as F
import math
from pathlib import Path
import sys
import unittest

import numpy as np
from hypothesis import given, settings, strategies as st

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [
    str(ROOT / "src"),
    str(ROOT.parent / "sovereign-clearing-audit/src"),
    str(ROOT.parent / "fire-sale-price-audit/src"),
]
from coupled import Economy, accounts, census, evaluate, _solve  # noqa: E402
from clearing import Network, rational_clear  # noqa: E402
from market import Market, equilibria  # noqa: E402


class CoupledTests(unittest.TestCase):
    def setUp(self):
        self.e = Economy(
            ((0.0, 0.1), (0.1, 0.0)), (0.1, 0.1), (0.0, 0.02), (1.0, 0.2), 0.8
        )

    def test_analytical_asymmetric(self):
        roots = census(self.e)
        expected = [0.05, (0.92 - math.sqrt(0.3984)) / 2, (1 + math.sqrt(0.424)) / 2]
        self.assertEqual(len(roots), 3)
        for r, q in zip(roots, expected):
            self.assertAlmostEqual(r.price, q, places=12)
        self.assertAlmostEqual(roots[0].payments[0], 13 / 150)
        self.assertAlmostEqual(roots[0].payments[1], 11 / 150)
        self.assertAlmostEqual(accounts(self.e, roots[0])["outside_unpaid"], 0.12)

    def test_symmetric_previous_prices(self):
        e = replace(self.e, cash=(0.0, 0.0), stock=(1.0, 1.0))
        self.assertEqual([r.price for r in census(e)], [0.05, 0.2, 0.8])

    def test_fixed_price_and_nulls(self):
        for e in [
            replace(self.e, impact=0.0),
            replace(self.e, cash=(1.0, 1.0)),
            replace(self.e, stock=(0.0, 0.0)),
            replace(self.e, floor=1.0),
        ]:
            roots = census(e)
            self.assertEqual([r.price for r in roots], [1.0])
        e = Economy(((0.0,),), (0.0,), (0.0,), (1.0,), 0.8)
        self.assertEqual([r.price for r in census(e)], [1.0])

    def test_fold_and_resolution(self):
        e = Economy(((0.0,),), (0.3125,), (0.0,), (2.0,), 0.8)
        self.assertEqual([r.price for r in census(e)], [0.05, 0.5])
        with self.assertRaises(ArithmeticError):
            census(replace(e, outside=(0.25,), cash=(1e-300,), impact=1.0))

    def test_invalid_and_scope(self):
        for kwargs in [
            dict(outside=()),
            dict(cash=(0.0,)),
            dict(impact=math.nan),
            dict(stock=(-1.0, 1.0)),
            dict(floor=0.0),
            dict(floor=2.0),
            dict(outside=(0.00001, 0.00001)),
            dict(impact=101.0),
            dict(liabilities=((0.1, 0.1), (0.1, 0.0))),
        ]:
            with self.assertRaises(ValueError):
                replace(self.e, **kwargs)
        with self.assertRaises(ValueError):
            Economy(
                tuple((0.0,) * 5 for _ in range(5)),
                (0.1,) * 5,
                (0.0,) * 5,
                (1.0,) * 5,
                0.8,
            )
        for price, payments in [
            (0.0, (0.1, 0.1)),
            (math.nan, (0.1, 0.1)),
            (0.5, (0.1,)),
            (0.5, (-0.1, 0.1)),
            (0.5, (1.0, 1.0)),
        ]:
            with self.assertRaises(ValueError):
                evaluate(self.e, price, payments)
        with self.assertRaises(ArithmeticError):
            _solve([[F(0)]], [F(1)])

    @settings(max_examples=40, deadline=None, derandomize=True)
    @given(st.lists(st.integers(0, 20), min_size=6, max_size=6))
    def test_generated_payment_oracle_and_monotonicity(self, values):
        e = replace(
            self.e,
            cash=(values[0] / 100, values[1] / 100),
            stock=(values[2] / 10, values[3] / 10),
            impact=values[4] / 10,
        )
        net = Network(np.array(e.liabilities), np.array(e.outside))
        roots = census(e)
        for r in roots:
            exact = rational_clear(net, np.array(e.cash) + r.price * np.array(e.stock))
            self.assertLess(
                max(abs(float(p) - q) for p, q in zip(exact, r.payments)), 1e-10
            )
            self.assertLess(abs(accounts(e, r)["identity_error"]), 1e-10)
        richer = replace(e, cash=tuple(c + 0.01 for c in e.cash))
        self.assertGreaterEqual(census(richer)[-1].price + 1e-9, roots[-1].price)

    @settings(max_examples=30, deadline=None, derandomize=True)
    @given(st.integers(0, 30), st.integers(0, 30), st.integers(0, 20))
    def test_no_edges_reduces_previous_market(self, first, second, impact):
        e = replace(
            self.e,
            liabilities=((0.0, 0.0), (0.0, 0.0)),
            cash=(first / 100, second / 100),
            impact=impact / 10,
        )
        old = Market(e.cash, e.outside, e.stock, e.impact, e.fundamental, e.floor)
        new = census(e)
        prior = equilibria(old)
        self.assertEqual(len(new), len(prior))
        for r, p in zip(new, prior):
            self.assertAlmostEqual(r.price, p.price, places=10)

    def test_permutation(self):
        e = replace(
            self.e,
            outside=self.e.outside[::-1],
            cash=self.e.cash[::-1],
            stock=self.e.stock[::-1],
            liabilities=tuple(tuple(reversed(r)) for r in reversed(self.e.liabilities)),
        )
        for first, second in zip(census(self.e), census(e)):
            self.assertEqual(first.price, second.price)
            np.testing.assert_allclose(
                first.payments, second.payments[::-1], atol=1e-12
            )


if __name__ == "__main__":
    unittest.main()
