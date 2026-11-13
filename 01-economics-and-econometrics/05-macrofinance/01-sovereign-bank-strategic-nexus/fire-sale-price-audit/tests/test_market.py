"""Analytical counterexamples, generated invariants and edge cases."""

from dataclasses import replace
from pathlib import Path
import math
import sys
import unittest

from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from market import Market, balance, equilibria, iterate, sales, update


class MarketTests(unittest.TestCase):
    def setUp(self):
        self.m = Market((0.0, 0.0), (0.1, 0.1), (1.0, 1.0), 0.8)

    def test_three_analytical_roots(self):
        roots = equilibria(self.m)
        self.assertEqual([round(r.price, 12) for r in roots], [0.05, 0.2, 0.8])
        self.assertEqual([r.stability for r in roots], ["stable", "unstable", "stable"])
        self.assertAlmostEqual(balance(self.m, 0.05)["unpaid"], 0.1)

    def test_fold_and_sides(self):
        # Exact discriminant4e-32: two roots only2e-16 apart must not be merged.
        close = Market((0.0,), (0.4999999999999999,), (2.0,), 0.5000000000000001)
        with self.assertRaises(ArithmeticError):
            equilibria(close)
        with self.assertRaises(ArithmeticError):
            equilibria(Market((1e-300,), (0.25,), (2.0,), 1.0))
        fold = replace(self.m, debt=(0.15625, 0.15625))
        self.assertEqual([r.price for r in equilibria(fold)], [0.05, 0.5])
        self.assertEqual(equilibria(fold)[1].stability, "marginal/kink")
        self.assertEqual(len(equilibria(replace(fold, debt=(0.15625001,) * 2))), 1)
        self.assertEqual(len(equilibria(replace(fold, debt=(0.15624999,) * 2))), 3)

    def test_cash_no_impact_and_domain(self):
        for market in [
            replace(self.m, impact=0.0),
            replace(self.m, cash=(0.2, 0.2)),
            replace(self.m, holdings=(0.0, 0.0)),
            replace(self.m, floor=1.0),
        ]:
            self.assertEqual([r.price for r in equilibria(market)], [1.0])
        for market in [
            replace(self.m, debt=(0.5, 0.5), impact=0.1),
            replace(self.m, debt=(0.01, 0.4), impact=0.2),
        ]:
            self.assertTrue(all(r.residual < 1e-10 for r in equilibria(market)))

    def test_kink_duplicate(self):
        market = Market((0.0,), (0.25,), (1.0,), 0.25, floor=0.25)
        self.assertEqual(len(equilibria(market)), 1)
        market = Market((0.0,), (0.5,), (1.0,), 0.5, floor=0.05)
        self.assertEqual([r.price for r in equilibria(market)], [0.5])
        self.assertEqual(equilibria(market)[0].stability, "marginal/kink")

    def test_iteration_basins_and_budget(self):
        self.assertAlmostEqual(iterate(self.m, 1.0)[0], 0.8)
        self.assertEqual(iterate(self.m, 0.05)[0], 0.05)
        with self.assertRaises(RuntimeError):
            iterate(self.m, 1.0, budget=1)
        for kwargs in [dict(tolerance=0), dict(tolerance=math.nan), dict(budget=0)]:
            with self.assertRaises(ValueError):
                iterate(self.m, 1.0, **kwargs)

    def test_invalid(self):
        for kwargs in [
            dict(cash=()),
            dict(debt=(1.0,)),
            dict(impact=-1.0),
            dict(floor=0.0),
            dict(floor=2.0),
            dict(cash=(math.nan, 0.0)),
            dict(holdings=(math.inf, 1.0)),
            dict(fundamental=1e7),
        ]:
            with self.assertRaises(ValueError):
                replace(self.m, **kwargs)
        for q in [0.0, math.nan, 2.0]:
            with self.assertRaises(ValueError):
                sales(self.m, q)

    def test_identical_bank_split(self):
        split = Market((0.0,) * 4, (0.05,) * 4, (0.5,) * 4, 0.8)
        self.assertEqual(
            [r.price for r in equilibria(split)], [r.price for r in equilibria(self.m)]
        )

    @settings(max_examples=40, deadline=None, derandomize=True)
    @given(st.integers(0, 40), st.integers(0, 20))
    def test_unit_rescaling(self, debt, cash):
        m = replace(self.m, debt=(debt / 100,) * 2, cash=(cash / 100,) * 2)
        doubled = replace(
            m,
            debt=tuple(2 * d for d in m.debt),
            cash=tuple(2 * c for c in m.cash),
            holdings=tuple(2 * s for s in m.holdings),
            impact=m.impact / 2,
        )
        self.assertEqual(len(equilibria(m)), len(equilibria(doubled)))
        for first, second in zip(equilibria(m), equilibria(doubled)):
            self.assertAlmostEqual(first.price, second.price, places=10)

    @settings(max_examples=80, deadline=None, derandomize=True)
    @given(
        st.lists(
            st.tuples(st.integers(0, 30), st.integers(0, 40), st.integers(0, 20)),
            min_size=1,
            max_size=6,
        ),
        st.integers(0, 20),
    )
    def test_generated_invariants(self, banks, impact):
        m = Market(
            tuple(c / 100 for c, _, _ in banks),
            tuple(d / 100 for _, d, _ in banks),
            tuple(s / 10 for _, _, s in banks),
            impact / 10,
        )
        roots = equilibria(m)
        permuted = replace(
            m, cash=m.cash[::-1], debt=m.debt[::-1], holdings=m.holdings[::-1]
        )
        self.assertEqual(roots, equilibria(permuted))
        for root in roots:
            self.assertLess(abs(update(m, root.price) - root.price), 1e-10)
            b = balance(m, root.price)
            self.assertLess(abs(b["identity_error"]), 1e-10)
            self.assertGreaterEqual(b["unpaid"], -1e-10)
        richer = replace(m, cash=tuple(c + 0.1 for c in m.cash))
        self.assertGreaterEqual(equilibria(richer)[-1].price + 1e-10, roots[-1].price)


if __name__ == "__main__":
    unittest.main()
