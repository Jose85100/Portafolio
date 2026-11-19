import csv
from pathlib import Path
import unittest

from liquidity_ladder import liquidity_ladder, parse_money


class LiquidityLadderTests(unittest.TestCase):
    def setUp(self):
        self.args = dict(as_of="2026-01-01", through="2026-01-10", currency="COP", opening="100")
        path = Path(__file__).resolve().parent.parent / "04-sarl-liquidity/examples/flujos_sinteticos.csv"
        with path.open(encoding="utf-8", newline="") as file:
            self.rows = list(csv.DictReader(file))

    def test_synthetic_fixture_reconciles_and_finds_first_shortfall(self):
        result = liquidity_ladder(self.rows, **self.args)
        self.assertEqual(result["total_inflows"], "65.00")
        self.assertEqual(result["total_outflows"], "140.00")
        self.assertEqual(result["closing_balance"], "25.00")
        self.assertEqual(result["first_shortfall_date"], "2026-01-02")
        self.assertEqual(result["minimum_closing_balance"], "-10.00")
        self.assertEqual(result["minimum_closing_date"], "2026-01-02")
        self.assertEqual(result["minimum_initial_funding"], "10.00")
        self.assertEqual(result["buckets"][1]["closing_balance"], "-10.00")
        self.assertEqual(result["buckets"][1]["flow_ids"], ["cobro_1", "deposito_1"])
        self.assertEqual(result["buckets"][-1]["date"], self.args["through"])

    def test_exact_cents_and_empty_ladder(self):
        self.assertEqual(parse_money("0.29"), 29)
        result = liquidity_ladder([], **self.args)
        self.assertEqual(result["closing_balance"], "100.00")
        self.assertIsNone(result["first_shortfall_date"])
        self.assertEqual(len(result["buckets"]), 2)

    def test_input_order_does_not_change_result(self):
        self.assertEqual(liquidity_ladder(self.rows, **self.args),
                         liquidity_ladder(reversed(self.rows), **self.args))

    def test_zero_balance_is_not_a_shortfall(self):
        rows = [dict(flow_id="x", due_date="2026-01-01", currency="COP", amount="-100.00")]
        self.assertIsNone(liquidity_ladder(rows, **self.args)["first_shortfall_date"])

    def test_funding_is_minimal_and_ties_use_first_date(self):
        rows = [dict(flow_id="a", due_date="2026-01-02", currency="COP", amount="-110.01"),
                dict(flow_id="b", due_date="2026-01-04", currency="COP", amount="0")]
        result = liquidity_ladder(rows, **self.args)
        self.assertEqual(result["minimum_closing_date"], "2026-01-02")
        self.assertEqual(result["minimum_initial_funding"], "10.01")
        funded = liquidity_ladder(rows, **dict(self.args, opening="110.01"))
        self.assertIsNone(funded["first_shortfall_date"])
        insufficient = liquidity_ladder(rows, **dict(self.args, opening="110.00"))
        self.assertEqual(insufficient["first_shortfall_date"], "2026-01-02")

    def test_rejects_ambiguous_and_out_of_scope_data(self):
        mutations = [
            dict(self.rows[0], currency="USD"),
            dict(self.rows[0], due_date="2025-12-31"),
            dict(self.rows[0], due_date="2026-01-11"),
            dict(self.rows[0], amount="1.001"),
            dict(self.rows[0], amount="NaN"),
            dict(self.rows[0], flow_id=""),
            dict(self.rows[0], extra="unexpected"),
        ]
        for row in mutations:
            with self.subTest(row=row), self.assertRaises(ValueError):
                liquidity_ladder([row], **self.args)
        with self.assertRaises(ValueError):
            liquidity_ladder([self.rows[0], self.rows[0]], **self.args)
        with self.assertRaises(ValueError):
            liquidity_ladder([], **dict(self.args, opening="-1"))
        with self.assertRaises(ValueError):
            liquidity_ladder([], **dict(self.args, through="2025-12-31"))
        with self.assertRaises(ValueError):
            liquidity_ladder([], **dict(self.args, currency="cop"))


if __name__ == "__main__":
    unittest.main()
