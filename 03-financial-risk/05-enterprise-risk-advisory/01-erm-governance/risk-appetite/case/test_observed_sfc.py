import csv
import tempfile
import unittest
from pathlib import Path

from observed_sfc import build, select_one


class ObservedSfcTests(unittest.TestCase):
    def test_observed_base_and_scenario_shocks(self):
        values = {(r['scenario'], r['metric_id']): r for r in build()}
        self.assertAlmostEqual(values['base', 'mora']['value'], 5.75418335)
        self.assertAlmostEqual(values['base', 'liquidez']['value'], 174.391146)
        self.assertAlmostEqual(values['adverso', 'mora']['value'] - values['base', 'mora']['value'], 1.5)
        self.assertAlmostEqual(values['severo', 'liquidez']['value'] - values['base', 'liquidez']['value'], -50)
        self.assertEqual(values['base', 'concentracion']['status'], 'SIN DATO')

    def test_unique_key_enforced_and_missing_not_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'x.csv'
            with path.open('w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'value'])
                writer.writeheader()
                writer.writerows([{'id': '1', 'value': '2'}, {'id': '1', 'value': '3'}])
            with self.assertRaises(ValueError):
                select_one(path, {'id': '1'})
            with self.assertRaises(ValueError):
                select_one(path, {'id': '2'})


if __name__ == '__main__':
    unittest.main()
