import unittest
import numpy as np
import pandas as pd
import run


class PaymentRiskTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(11)
        count = 100
        df = pd.DataFrame({'ID': np.arange(count), 'LIMIT_BAL': np.full(count, 1000),
                           run.TARGET: np.arange(count) % 2})
        for col in run.FEATURES:
            df[col] = rng.integers(-2, 4, size=count)
        self.data = run.validate(df)

    def test_input_contract_rejects_duplicate_and_invalid(self):
        bad = self.data.copy()
        bad.loc[0, 'ID'] = 1
        with self.assertRaises(ValueError):
            run.validate(bad)
        bad = self.data.copy()
        bad.loc[0, run.TARGET] = 2
        with self.assertRaises(ValueError):
            run.validate(bad)
        bad = self.data.copy()
        bad.loc[0, 'PAY_0'] = np.nan
        with self.assertRaises(ValueError):
            run.validate(bad)

    def test_heldout_conservation_and_determinism(self):
        train, test = self.data.iloc[:80], self.data.iloc[80:]
        a = run.evaluate(train, test, bootstrap=50)
        b = run.evaluate(train, test, bootstrap=50)
        self.assertEqual(a, b)
        self.assertEqual(sum(x['n'] for x in a['calibration_bins']), len(test))
        self.assertAlmostEqual(a['default_label_weighted_proxy_loss_twd'], 10 * 1000 * .45)
        self.assertAlmostEqual(a['baseline']['brier'] - a['model']['brier'], a['brier_improvement_baseline_minus_model'])

    def test_exposure_not_used_to_fit_model(self):
        train, test = self.data.iloc[:80].copy(), self.data.iloc[80:].copy()
        a = run.evaluate(train, test, bootstrap=20)
        test['LIMIT_BAL'] *= 2
        b = run.evaluate(train, test, bootstrap=20)
        self.assertEqual(a['model'], b['model'])
        self.assertAlmostEqual(2 * a['expected_proxy_loss_twd'], b['expected_proxy_loss_twd'])
        self.assertAlmostEqual(2 * a['default_label_weighted_proxy_loss_twd'], b['default_label_weighted_proxy_loss_twd'])

    def test_missing_class_is_error(self):
        train, test = self.data.iloc[:80].copy(), self.data.iloc[80:].copy()
        train[run.TARGET] = 0
        with self.assertRaises(ValueError):
            run.evaluate(train, test, bootstrap=20)


if __name__ == '__main__':
    unittest.main()
