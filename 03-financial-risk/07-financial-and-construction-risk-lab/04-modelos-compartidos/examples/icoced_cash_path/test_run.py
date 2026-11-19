import csv
from pathlib import Path
import unittest
import run


class IndexScenarioTests(unittest.TestCase):
    def setUp(self):
        with run.SOURCE.open(encoding='utf-8', newline='') as f:
            self.rows = list(csv.DictReader(f))

    def test_observed_windows_and_contract(self):
        result = run.scenarios(self.rows)
        self.assertEqual(len(result), 34)
        self.assertEqual(sum(r['first_breach_period'] is not None for r in result), 10)
        self.assertAlmostEqual(max(r['minimum_funding_cop_millions'] for r in result), 11.1487764009)

    def test_share_sensitivity_and_validation(self):
        no_exposure = run.scenarios(self.rows, cost_share=0)
        self.assertTrue(all(r['minimum_funding_cop_millions'] == 0 for r in no_exposure))
        with self.assertRaises(ValueError):
            run.scenarios(self.rows, cost_share=-0.1)
        with self.assertRaises(ValueError):
            run.scenarios(self.rows, months=1.5)

    def test_missing_or_duplicate_month_rejected(self):
        rows = [r for r in self.rows if not (r['input'] == 'Concreto común' and r['period'] == '2022-01-01')]
        with self.assertRaises(ValueError):
            run.scenarios(rows)


if __name__ == '__main__':
    unittest.main()
