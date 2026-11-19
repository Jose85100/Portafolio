import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import run


class SouthGermanBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = run.load_data()

    def test_canonical_dataset_and_labels(self):
        self.assertEqual(len(self.data), 1000)
        self.assertEqual(int((self.data.kredit == 0).sum()), 300)
        self.assertEqual(int((self.data.kredit == 1).sum()), 700)

    def test_split_target_and_reproducibility(self):
        a, b = train_test_split(self.data, test_size=.25, random_state=42, stratify=self.data.kredit)
        self.assertTrue(set(a.index).isdisjoint(set(b.index)))
        r = run.evaluate(a, b, bootstrap=10)
        self.assertEqual((r['train_n'], r['test_n']), (750, 250))
        self.assertEqual(r['test_bad_rate'], .3)
        self.assertEqual(r, run.evaluate(a, b, bootstrap=10))
        self.assertEqual(sum(x['n'] for x in r['calibration_groups']), 250)

    def test_reject_malformed_data(self):
        bad = self.data.copy()
        bad.loc[bad.index[0], 'laufkont'] = 9
        with self.assertRaises(ValueError): run.validate(bad)
        bad = self.data.copy()
        bad['laufzeit'] = bad['laufzeit'].astype(float)
        bad.loc[bad.index[0], 'laufzeit'] = np.inf
        with self.assertRaises(ValueError): run.validate(bad)
        with self.assertRaises(ValueError): run.load_data(Path(__file__))

    def test_no_outcome_or_protected_features(self):
        self.assertFalse(set(run.FEATURES) & {'kredit', 'famges', 'alter', 'gastarb'})
        a, b = train_test_split(self.data, test_size=.25, random_state=42, stratify=self.data.kredit)
        original = run.evaluate(a, b, bootstrap=10)
        modified = b.copy()
        modified['famges'] = 0
        self.assertEqual(original, run.evaluate(a, modified, bootstrap=10))


if __name__ == '__main__':
    unittest.main()
