import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from risk_models import project_cash_path


class CashPathTests(unittest.TestCase):
    def test_shortfall_and_recovery(self):
        r = project_cash_path([5, -8, 10], [2, 2, 2], initial_cash=3, liquidity_floor=1)
        self.assertEqual(r["cash_path"], [6, -4, 4])
        self.assertEqual(r["first_breach_period"], 2)
        self.assertEqual(r["minimum_funding"], 5)
        self.assertEqual(r["minimum_dscr"], -4)

    def test_initial_breach_and_zero_debt(self):
        r = project_cash_path([2], [0], initial_cash=0, liquidity_floor=1)
        self.assertEqual(r["first_breach_period"], 0)
        self.assertEqual(r["minimum_funding"], 1)
        self.assertEqual(r["dscr"], [None])

    def test_floor_is_not_a_breach(self):
        self.assertIsNone(project_cash_path([0], [0], 1, 1)["first_breach_period"])

    def test_invalid(self):
        for cf, debt in [([1], [1, 2]), ([1], [-1]), ([float("nan")], [0])]:
            with self.assertRaises(ValueError):
                project_cash_path(cf, debt)


if __name__ == "__main__":
    unittest.main()
