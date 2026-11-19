import unittest
import pandas as pd
import run


class UCIContractTests(unittest.TestCase):
    def test_split_and_no_overlap(self):
        frame = pd.DataFrame({'ID': range(30000), 'LIMIT_BAL': [100] * 30000,
                              'default payment next month': [0, 1] * 15000})
        train, test = run.prepare(frame)
        self.assertEqual((len(train), len(test)), (22500, 7500))
        self.assertTrue(set(train.ID).isdisjoint(set(test.ID)))
        self.assertEqual(run.prepare(frame)[0].ID.tolist(), train.ID.tolist())

    def test_segments_fit_on_training_only(self):
        train = pd.DataFrame({'LIMIT_BAL': [1, 2, 3, 4, 5, 6],
                              'default payment next month': [0, 0, 1, 1, 0, 1]})
        test = pd.DataFrame({'LIMIT_BAL': [1, 3, 6],
                             'default payment next month': [1, 0, 0]})
        cuts, rates, predicted = run.segment_pd(train, test)
        self.assertEqual(rates, [0.0, 1.0, 0.5])
        self.assertEqual(list(predicted), [0.0, 1.0, 0.5])
        test['default payment next month'] = [0, 1, 1]
        self.assertEqual(list(run.segment_pd(train, test)[2]), list(predicted))

    def test_invalid_label_and_duplicate(self):
        frame = pd.DataFrame({'ID': range(30000), 'LIMIT_BAL': [100] * 30000,
                              'default payment next month': [0] * 30000})
        frame.loc[0, 'default payment next month'] = 2
        with self.assertRaises(ValueError):
            run.prepare(frame)
        frame.loc[0, 'default payment next month'] = 0
        frame.loc[0, 'ID'] = 1
        with self.assertRaises(ValueError):
            run.prepare(frame)


if __name__ == '__main__':
    unittest.main()
