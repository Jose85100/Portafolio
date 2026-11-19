import csv
import json
import unittest

from historical_sfc import HERE, ICV, IRL, calculate, months, read_csv


class HistoricalSfcTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((HERE / 'config.json').read_text(encoding='utf-8'))

    def test_observed_coverage_and_reproduction(self):
        rows = calculate(read_csv(IRL), read_csv(ICV), self.config)
        self.assertEqual((len(rows), rows[0]['period'], rows[-1]['period']), (34, '2020-03-31', '2022-12-31'))
        self.assertAlmostEqual(rows[-1]['mora_value_pct'], 5.75418335)
        self.assertAlmostEqual(rows[-1]['liquidez_value_pct'], 174.391146)
        self.assertTrue(all(row['concentracion_status'] == 'SIN DATO' for row in rows))
        with (HERE / 'historical_sfc_results.csv').open(encoding='utf-8', newline='') as f:
            saved = list(csv.DictReader(f))
        self.assertEqual(len(saved), len(rows))
        for expected, actual in zip(rows, saved):
            self.assertEqual(expected['period'], actual['period'])
            self.assertEqual(expected['mora_status'], actual['mora_status'])
            self.assertEqual(expected['liquidez_status'], actual['liquidez_status'])
            self.assertEqual(expected['mora_consecutive_breaches'], int(actual['mora_consecutive_breaches']))
            self.assertAlmostEqual(expected['mora_value_pct'], float(actual['mora_value_pct']))

    def test_gap_does_not_carry_or_join_to_next_month(self):
        periods = months((2022, 10), (2022, 12))
        irl = [{'entity_code': '1-1', 'period': p, 'irl_pct_reported': '100'} for p in (periods[0], periods[2])]
        icv = [{'entity_type_code': '1', 'entity_code': '1', 'modality': 'Consumo', 'period': p, 'icv_reported_pct': '7'} for p in periods]
        result = calculate(irl, icv, self.config, periods)
        self.assertEqual([x['liquidez_status'] for x in result], ['BRECHA', 'SIN DATO', 'BRECHA'])
        self.assertEqual([x['liquidez_consecutive_breaches'] for x in result], [1, 0, 1])
        self.assertEqual([x['mora_consecutive_breaches'] for x in result], [1, 2, 3])

    def test_missing_period_in_calendar_rejected(self):
        with self.assertRaises(ValueError):
            calculate([], [], self.config, ['2022-10-31', '2022-12-31'])

    def test_duplicate_key_rejected(self):
        period = '2022-12-31'
        row = {'entity_code': '1-1', 'period': period, 'irl_pct_reported': '100'}
        with self.assertRaises(ValueError):
            calculate([row, row], [], self.config, [period])


if __name__ == '__main__':
    unittest.main()
