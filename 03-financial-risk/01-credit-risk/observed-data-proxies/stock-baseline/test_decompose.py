import unittest
from decompose import pair, phase_snapshots


def group(total, late, departments=('A',)):
    return {'total': total, 'late': late, 'departments': set(departments)}


class DecompositionTests(unittest.TestCase):
    def test_rate_only(self):
        before = {'ESTUDIOS': group(50, 5), 'AMORTIZACION': group(50, 10)}
        after = {'ESTUDIOS': group(50, 10), 'AMORTIZACION': group(50, 15)}
        result = pair(before, after)
        self.assertAlmostEqual(result['change_pp'], 10)
        self.assertAlmostEqual(result['rate_effect_pp'], 10)
        self.assertAlmostEqual(result['mix_effect_pp'], 0)

    def test_mix_only_and_coverage(self):
        before = {'ESTUDIOS': group(50, 5), 'AMORTIZACION': group(50, 10)}
        after = {'ESTUDIOS': group(20, 2, ('B',)), 'AMORTIZACION': group(80, 16)}
        result = pair(before, after)
        self.assertAlmostEqual(result['change_pp'], 3)
        self.assertAlmostEqual(result['rate_effect_pp'], 0)
        self.assertAlmostEqual(result['mix_effect_pp'], 3)
        self.assertEqual(result['phases'][1]['departments_added'], ['B'])
        self.assertEqual(result['phases'][1]['departments_removed'], ['A'])

    def test_missing_phase_or_invalid_count(self):
        with self.assertRaises(ValueError):
            pair({'A': group(10, 2)}, {'B': group(10, 2)})
        with self.assertRaises(ValueError):
            pair({'A': group(10, 20)}, {'A': group(10, 2)})
        with self.assertRaises(ValueError):
            phase_snapshots([{'fecha_corte': '2024-03-31', 'epoca_cartera': 'ESTUDIOS',
                              'departamento': 'A', 'creditos_total': '1',
                              'creditos_mora_mayor_90d': '0', 'evidencia': 'OBSERVADO_AGREGADO'}])


if __name__ == '__main__':
    unittest.main()
