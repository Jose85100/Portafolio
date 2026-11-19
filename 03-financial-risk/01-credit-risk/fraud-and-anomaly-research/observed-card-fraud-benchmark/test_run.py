import unittest
import numpy as np
import pandas as pd
from run import FEATURES, temporal_split, topk_metrics, validate


class BenchmarkTests(unittest.TestCase):
    def test_time_boundaries_not_split(self):
        d = {name: np.ones(20) for name in FEATURES}
        d.update(Time=np.repeat(np.arange(10), 2), Class=np.tile([0, 1], 10))
        d = pd.DataFrame(d)[['Time', *FEATURES, 'Class']]
        validate(d, full=False)
        train, valid, test = temporal_split(d)
        self.assertLess(train.Time.max(), valid.Time.min())
        self.assertLess(valid.Time.max(), test.Time.min())
        self.assertEqual((len(train), len(valid), len(test)), (12, 4, 4))

    def test_ties_and_exact_capacity(self):
        result = topk_metrics([1, 0, 1, 0], [2, 2, 2, 1], .5)
        self.assertEqual(result['alerts'], 2)
        self.assertEqual(result['true_positives'], 1)
        self.assertEqual(result['precision'], .5)
        self.assertEqual(result['recall'], .5)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            topk_metrics([0, 1], [float('nan'), 0], .5)
        with self.assertRaises(ValueError):
            topk_metrics([0, 2], [0, 1], .5)
        with self.assertRaises(ValueError):
            topk_metrics([0, 1], [0, 1], 0)


if __name__ == '__main__':
    unittest.main()
