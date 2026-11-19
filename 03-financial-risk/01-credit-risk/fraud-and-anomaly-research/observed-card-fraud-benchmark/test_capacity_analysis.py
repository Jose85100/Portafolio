import unittest
from capacity_analysis import choose_threshold, fixed_threshold_metrics, evaluate


class CapacityTests(unittest.TestCase):
    def test_threshold_fixed_from_validation_and_ties(self):
        threshold = choose_threshold([1, 2, 2, 3], .5)
        self.assertEqual(threshold, 2)
        r = fixed_threshold_metrics([0, 1, 0, 1], [1, 2, 2, 3], threshold)
        self.assertEqual((r['alerts'], r['true_positives'], r['false_positives']), (3, 2, 1))
        self.assertEqual((r['precision'], r['recall']), (2/3, 1))

    def test_null_precision_and_recall(self):
        r = fixed_threshold_metrics([0, 0], [0.1, 0.2], .5)
        self.assertIsNone(r['precision'])
        self.assertIsNone(r['recall'])
        self.assertEqual(r['false_negatives'], 0)

    def test_validation_threshold_does_not_depend_on_test_labels(self):
        a = evaluate([0, 1, 0], [0.1, 0.9, 0.4], [0, 1], [0.8, 0.2])
        b = evaluate([0, 1, 0], [0.1, 0.9, 0.4], [1, 0], [0.8, 0.2])
        self.assertEqual(a['validation_threshold_1pct'], b['validation_threshold_1pct'])
        self.assertEqual(a['test_fixed_threshold']['alerts'], b['test_fixed_threshold']['alerts'])

    def test_reject_bad_inputs(self):
        for s, f in [([], .1), ([float('nan')], .1), ([1], 0)]:
            with self.assertRaises(ValueError):
                choose_threshold(s, f)
        with self.assertRaises(ValueError):
            fixed_threshold_metrics([0, 2], [1, 2], 1)

if __name__ == '__main__':
    unittest.main()
