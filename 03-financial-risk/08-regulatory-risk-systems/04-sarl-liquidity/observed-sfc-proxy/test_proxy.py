import csv
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest

from run import load_snapshot, scenario, verify_snapshot, SCENARIOS, SOURCE, PDF


class SfcProxyTests(unittest.TestCase):
    def test_snapshot_integrity_and_tampering(self):
        verify_snapshot()
        with tempfile.TemporaryDirectory() as td:
            changed = Path(td) / 'changed.csv'
            changed.write_bytes(SOURCE.read_bytes() + b'\n')
            with self.assertRaises(ValueError):
                verify_snapshot(changed, PDF)
    def test_known_source_and_amount_units(self):
        alm, rln = load_snapshot()
        self.assertEqual((alm, rln), (Decimal('160953536'), Decimal('90040630')))
        result = scenario(alm, rln, Decimal('.6'), Decimal('1'))
        self.assertEqual(result['opening_balance'], '96572121600000.00')
        self.assertEqual(result['total_outflows'], '90040630000000.00')
        self.assertEqual(result['closing_balance'], '6531491600000.00')
        self.assertIsNone(result['first_shortfall_date'])

    def test_scenarios_order_and_shortfalls(self):
        alm, rln = load_snapshot()
        results = {name: scenario(alm, rln, *params) for name, params in SCENARIOS.items()}
        self.assertEqual(results['adverso']['first_shortfall_date'], '2026-12-01')
        self.assertEqual(results['severo']['first_shortfall_date'], '2026-11-21')
        self.assertLess(Decimal(results['severo']['closing_balance']), Decimal(results['adverso']['closing_balance']))
        for result in results.values():
            self.assertEqual(Decimal(result['opening_balance']) - Decimal(result['total_outflows']),
                             Decimal(result['closing_balance']))

    def test_missing_duplicate_and_invalid_source(self):
        row = {'period': '2026-08-31', 'entity_type': 'Bancos', 'alm_million_cop': '1', 'rln_30d_million_cop': '2'}
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'source.csv'
            def write(rows):
                with path.open('w', newline='', encoding='utf8') as stream:
                    w = csv.DictWriter(stream, fieldnames=list(row))
                    w.writeheader(); w.writerows(rows)
            for rows in ([], [row, row], [{**row, 'rln_30d_million_cop': '0'}], [{**row, 'alm_million_cop': 'NaN'}]):
                write(rows)
                with self.assertRaises(ValueError):
                    load_snapshot(path)

    def test_reject_invalid_assumptions(self):
        for fraction, multiple in [('-0.1', '1'), ('1.1', '1'), ('0.6', '-1'), ('NaN', '1')]:
            with self.assertRaises(ValueError):
                scenario(Decimal(1), Decimal(1), Decimal(fraction), Decimal(multiple))


if __name__ == '__main__':
    unittest.main()
