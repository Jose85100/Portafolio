import csv
import math
import unittest
from run import SOURCE, transitions, fit, evaluate, score, state, cluster_interval


def observation(entity, date, ratio, rln=100):
    return {'entity_code': entity, 'period': date, 'irl_pct_reported': str(ratio),
            'rln_30d_average_thousand_cop': str(rln)}


class TransitionTests(unittest.TestCase):
    def test_boundaries_and_gaps(self):
        self.assertEqual([state(x) for x in (149.999, 150, 249.999, 250)], [0, 1, 1, 2])
        records = [observation('A', '2021-01-31', 149), observation('A', '2021-03-31', 251),
                   observation('A', '2021-04-30', 250)]
        pairs = transitions(records)
        self.assertEqual(len(pairs), 1)
        self.assertEqual((pairs[0]['from'], pairs[0]['to']), (2, 2))

    def test_manual_smoothing_and_score(self):
        train = [{'from': 0, 'to': 0}, {'from': 0, 'to': 1}, {'from': 1, 'to': 1}]
        model = fit(train, alpha=0.5)
        self.assertAlmostEqual(model['transition'][0][0], 1.5 / 3.5)
        self.assertAlmostEqual(sum(model['transition'][0]), 1)
        self.assertAlmostEqual(model['pooled_switch_rate'], 1.5 / 4)
        sample = {'from': 0, 'to': 1}
        brier, logloss = score(model, sample, 'transition')
        p = model['transition'][0]
        self.assertAlmostEqual(brier, p[0] ** 2 + (p[1] - 1) ** 2 + p[2] ** 2)
        self.assertAlmostEqual(logloss, -math.log(p[1]))

    def test_contracts(self):
        row = observation('A', '2022-01-31', 120)
        with self.assertRaises(ValueError): transitions([row, row])
        with self.assertRaises(ValueError): transitions([observation('A', '2022-01-31', 120, 0)])
        with self.assertRaises(ValueError): fit([], 0.5)
        with self.assertRaises(ValueError): fit([{'from': 0, 'to': 0}], 0)
        with self.assertRaises(ValueError): evaluate(fit([{'from': 0, 'to': 0}]), [])

    def test_observed_split_and_cluster_determinism(self):
        with SOURCE.open(encoding='utf-8', newline='') as f: pairs = transitions(csv.DictReader(f))
        train = [p for p in pairs if p['period'][:7] <= '2021-12']
        test = [p for p in pairs if '2022-01' <= p['period'][:7] <= '2022-12']
        self.assertEqual((len(train), len(test)), (868, 521))
        model = fit(train)
        self.assertEqual(cluster_interval(model, test, 10, 42), cluster_interval(model, test, 10, 42))
        self.assertTrue(all(abs(sum(row) - 1) < 1e-12 for row in model['transition']))


if __name__ == '__main__':
    unittest.main()
