import csv
import math
import unittest
import run


def row(month, value, entity='bank'):
    return {'entity_code': entity, 'period': month, 'irl_pct_reported': str(value),
            'rln_30d_average_thousand_cop': '100'}


class BenchmarkTests(unittest.TestCase):
    def test_known_forecasts_and_error_sign(self):
        data = [row('2021-10-31', 100), row('2021-11-30', 130),
                row('2021-12-31', 160), row('2022-01-31', 190)]
        pairs, eligible = run.build(data)
        self.assertEqual(eligible, 1)
        self.assertEqual(pairs[0]['carry_pct'], 160)
        self.assertEqual(pairs[0]['ma3_pct'], 130)
        self.assertEqual(pairs[0]['ma3_error_pp'], -60)
        self.assertEqual(run.metrics(pairs, 'carry_error_pp')['mae_pp'], 30)

    def test_missing_prior_month_not_carried_over(self):
        data = [row('2021-10-31', 100), row('2021-12-31', 160), row('2022-01-31', 190),
                row('2021-10-31', 200, 'other'), row('2021-11-30', 200, 'other'),
                row('2021-12-31', 200, 'other'), row('2022-01-31', 210, 'other')]
        pairs, eligible = run.build(data)
        self.assertEqual(eligible, 2)
        self.assertEqual([x['entity_code'] for x in pairs], ['other'])

    def test_rejects_duplicates_and_invalid_values(self):
        base = [row('2021-12-31', 10)]
        with self.assertRaises(ValueError):
            run.build(base * 2)
        with self.assertRaises(ValueError):
            run.build([row('2021-12-31', math.nan)])

    def test_observed_snapshot_and_no_lookahead(self):
        with run.SOURCE.open(encoding='utf-8', newline='') as f:
            source = list(csv.DictReader(f))
        pairs, eligible = run.build(source)
        self.assertEqual((len(pairs), eligible), (515, 525))
        item = next(x for x in pairs if x['period'] == '2022-01-31')
        modified = [dict(x) for x in source]
        for r in modified:
            if r['period'] >= '2022-01-31':
                r['irl_pct_reported'] = '100'
        new, _ = run.build(modified)
        other = next(x for x in new if x['period'] == item['period'] and x['entity_code'] == item['entity_code'])
        self.assertEqual(item['carry_pct'], other['carry_pct'])
        self.assertEqual(item['ma3_pct'], other['ma3_pct'])


if __name__ == '__main__':
    unittest.main()
