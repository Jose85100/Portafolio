import copy
import csv
import json
from pathlib import Path
import unittest

from appetite import evaluate, report

HERE = Path(__file__).parent


class AppetiteTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((HERE / "config.json").read_text())
        with (HERE / "observations.csv").open(newline="") as source:
            self.rows = list(csv.DictReader(source))

    def test_fixture_and_missing_data(self):
        result = {(r["scenario"], r["metric_id"]): r for r in evaluate(self.config, self.rows)}
        self.assertEqual(result["base", "mora"]["status"], "NORMAL")
        self.assertEqual(result["adverso", "liquidez"]["status"], "ALERTA")
        self.assertEqual(result["severo", "liquidez"]["status"], "BRECHA")
        self.assertEqual(result["severo", "concentracion"]["status"], "SIN DATO")
        self.assertIn("SIN DATO", report(list(result.values())))

    def test_equal_thresholds_count_and_directions(self):
        rows = copy.deepcopy(self.rows)
        for row in rows:
            if row["scenario"] == "base" and row["metric_id"] == "mora":
                row["value"] = "4"
            if row["scenario"] == "base" and row["metric_id"] == "liquidez":
                row["value"] = "110"
        result = {(r["scenario"], r["metric_id"]): r["status"] for r in evaluate(self.config, rows)}
        self.assertEqual(result["base", "mora"], "ALERTA")
        self.assertEqual(result["base", "liquidez"], "BRECHA")

    def test_bad_data_rejected(self):
        for invalid in ("NaN", "inf", "abc", "", "-1", "101"):
            rows = copy.deepcopy(self.rows)
            rows[0]["value"] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                evaluate(self.config, rows)
        for change in ({"unit": "COP"}, {"metric_id": "other"}, {"scenario": "other"}):
            rows = copy.deepcopy(self.rows)
            rows[0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                evaluate(self.config, rows)
        with self.assertRaises(ValueError):
            evaluate(self.config, self.rows + self.rows[:1])

    def test_bad_threshold_order_and_duplicate_definition(self):
        config = copy.deepcopy(self.config)
        config["metrics"][0]["warning"] = config["metrics"][0]["limit"]
        with self.assertRaises(ValueError):
            evaluate(config, self.rows)
        config = copy.deepcopy(self.config)
        config["metrics"].append(copy.deepcopy(config["metrics"][0]))
        with self.assertRaises(ValueError):
            evaluate(config, self.rows)


if __name__ == "__main__":
    unittest.main()
