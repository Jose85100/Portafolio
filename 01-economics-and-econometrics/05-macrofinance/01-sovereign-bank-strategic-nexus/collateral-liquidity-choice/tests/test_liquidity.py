import sys
from pathlib import Path
import unittest

from hypothesis import given, settings, strategies as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from liquidity import Problem, dense_grid, evaluate, liquidation_only, solve  # noqa: E402


class LiquidityChoiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.main = Problem(0.4, 1.0, 1.0, 0.5, 0.1, 0.3, 0.1)

    def test_main_mixed_choice_beats_liquidation(self) -> None:
        optimal, baseline = solve(self.main), liquidation_only(self.main)
        self.assertGreater(optimal.borrowing, 0)
        self.assertLess(optimal.liquidation, baseline.liquidation)
        self.assertLess(optimal.cost, baseline.cost)
        self.assertAlmostEqual(optimal.collateral_slack, 0.0, places=9)

    def test_dense_grid_oracle(self) -> None:
        exact, grid = solve(self.main), dense_grid(self.main, 200_001)
        self.assertLessEqual(abs(exact.liquidation - grid.liquidation), 1e-5)
        self.assertLessEqual(abs(exact.cost - grid.cost), 1e-5)

    def test_borrow_only_when_borrowing_is_free(self) -> None:
        choice = solve(Problem(0.4, 1, 1, 0.5, 0.1, 0.8, 0.0))
        self.assertEqual(choice.liquidation, 0)
        self.assertEqual(choice.borrowing, 0.4)

    def test_high_rate_selects_liquidation(self) -> None:
        choice = solve(Problem(0.4, 1, 1, 0.5, 0.1, 0.8, 2.0))
        self.assertAlmostEqual(choice.borrowing, 0.0, places=9)

    def test_no_price_impact(self) -> None:
        choice = solve(Problem(0.4, 1, 1, 0, 0.1, 0.3, 0.1))
        self.assertAlmostEqual(choice.liquidation, 0.4, places=9)
        self.assertAlmostEqual(choice.borrowing, 0.0, places=9)

    def test_infeasible_and_invalid(self) -> None:
        with self.assertRaises(ArithmeticError):
            solve(Problem(2, 1, 1, 0.5, 0.1, 0.3, 0.1))
        with self.assertRaises(ArithmeticError):
            liquidation_only(Problem(2, 1, 1, 0.5, 0.1, 0.3, 0.1))
        with self.assertRaises(ValueError):
            Problem(-1, 1, 1, 0.5, 0.1, 0.3, 0.1)
        with self.assertRaises(ValueError):
            Problem(1, 1, float("nan"), 0.5, 0.1, 0.3, 0.1)
        with self.assertRaises(ValueError):
            evaluate(self.main, 2)
        with self.assertRaises(ValueError):
            dense_grid(self.main, 1)

    @settings(max_examples=60, deadline=None)
    @given(
        shortfall=st.floats(0.05, 0.45, allow_nan=False, allow_infinity=False),
        pledgeable=st.floats(0.15, 1, allow_nan=False, allow_infinity=False),
        rate=st.floats(0, 2, allow_nan=False, allow_infinity=False),
    )
    def test_solution_is_feasible_and_not_worse_than_grid(
        self, shortfall: float, pledgeable: float, rate: float
    ) -> None:
        problem = Problem(shortfall, 1, 1, 0.4, 0.1, pledgeable, rate)
        optimal = solve(problem)
        grid = dense_grid(problem, 2_001)
        self.assertGreaterEqual(optimal.collateral_slack, -1e-9)
        self.assertGreaterEqual(optimal.liquidity_slack, -1e-9)
        self.assertLessEqual(optimal.cost, grid.cost + 1e-8)

    @settings(max_examples=40, deadline=None)
    @given(scale=st.floats(0.1, 20, allow_nan=False, allow_infinity=False))
    def test_monetary_scale_invariance(self, scale: float) -> None:
        base = solve(self.main)
        scaled = solve(Problem(0.4 * scale, scale, 1, 0.5 / scale, 0.1, 0.3, 0.1))
        self.assertAlmostEqual(scaled.liquidation / scale, base.liquidation, places=8)
        self.assertAlmostEqual(scaled.borrowing / scale, base.borrowing, places=8)


if __name__ == "__main__":
    unittest.main()
