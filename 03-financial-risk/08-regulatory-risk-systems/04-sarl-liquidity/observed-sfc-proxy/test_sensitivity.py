from decimal import Decimal
import unittest
from sensitivity import sensitivity


class SensitivityTests(unittest.TestCase):
    def test_grid_and_monotonicity(self):
        rows = sensitivity(Decimal('160953536'), Decimal('90040630'))
        self.assertEqual(len(rows), 9)
        for fraction in ('0.40', '0.60', '0.80'):
            subset = [r for r in rows if r['usable_alm_fraction'] == fraction]
            values = [Decimal(r['minimum_initial_funding_cop']) for r in subset]
            self.assertEqual(values, sorted(values))
        for multiple in ('1.00', '1.50', '2.00'):
            subset = [r for r in rows if r['rln_multiple'] == multiple]
            values = [Decimal(r['minimum_initial_funding_cop']) for r in subset]
            self.assertEqual(values, sorted(values, reverse=True))
        base = next(r for r in rows if r['usable_alm_fraction'] == '0.60' and r['rln_multiple'] == '1.00')
        self.assertEqual(base['minimum_initial_funding_cop'], '0.00')
        severe = next(r for r in rows if r['usable_alm_fraction'] == '0.60' and r['rln_multiple'] == '2.00')
        self.assertEqual(severe['minimum_initial_funding_cop'], '83509138400000.00')

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            sensitivity(Decimal(1), Decimal(1), fractions=())
        with self.assertRaises(ValueError):
            sensitivity(Decimal(1), Decimal(1), fractions=(Decimal('-0.1'),))


if __name__ == '__main__':
    unittest.main()
