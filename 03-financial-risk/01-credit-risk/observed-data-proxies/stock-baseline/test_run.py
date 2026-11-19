from datetime import date
import unittest
from run import summarize, evaluate


def row(dept='A', d='2023-12-31', total=100, late=20):
    return {'fecha_corte': d, 'epoca_cartera': 'ESTUDIOS', 'departamento': dept,
            'creditos_total': str(total), 'creditos_mora_mayor_90d': str(late),
            'evidencia': 'OBSERVADO_AGREGADO'}


class StockBaselineTests(unittest.TestCase):
    def test_weighted_counts_not_mean_of_rates(self):
        points = summarize([row('A', total=10, late=5), row('B', total=90, late=0)])
        self.assertAlmostEqual(points[0][2], 0.05)

    def test_duplicates_and_invalid_counts(self):
        with self.assertRaises(ValueError):
            summarize([row(), row()])
        with self.assertRaises(ValueError):
            summarize([row(total=1, late=2)])

    def test_previous_quarter_and_gap(self):
        dates = ['2023-03-31', '2023-06-30', '2023-09-30', '2023-12-31',
                 '2024-03-31', '2024-09-30', '2024-12-31']
        points = [(date.fromisoformat(x), 'ESTUDIOS', i / 100) for i, x in enumerate(dates)]
        predictions, metrics = evaluate(points)
        self.assertEqual([x['fecha_corte'] for x in predictions], ['2024-03-31', '2024-12-31'])
        self.assertEqual(predictions[0]['previous_quarter'], 0.03)
        self.assertEqual(metrics['ESTUDIOS']['n'], 2)

    def test_reject_nonquarter_and_duplicate(self):
        with self.assertRaises(ValueError):
            evaluate([(date(2024, 1, 1), 'ESTUDIOS', 0.1)])
        with self.assertRaises(ValueError):
            evaluate([(date(2024, 3, 31), 'ESTUDIOS', 0.1)] * 2)


if __name__ == '__main__':
    unittest.main()
