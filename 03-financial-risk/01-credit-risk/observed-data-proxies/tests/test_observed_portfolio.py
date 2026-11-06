import importlib.util
import pathlib
import unittest
from datetime import date

path = pathlib.Path(__file__).resolve().parents[1] / "src" / "observed_portfolio.py"
spec = importlib.util.spec_from_file_location("observed_portfolio", path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def record(**updates):
    x = dict(fecha_corte="2025-01-31T00:00:00", deptoresidencia="Bogota",
             cantidad_creditos_al_dia="80", cantidad_creditos_con_mora="15",
             cantidad_creditos_mora_mayor="5", total_creditos="100",
             indicador_cartera_vencida="4.2", epoca_cartera="AMORTIZACION")
    x.update(updates)
    return x


class ObservedDataTests(unittest.TestCase):
    def test_mora_share_is_not_pd(self):
        x = m.normalized(record(), date(2025, 1, 31))
        self.assertEqual(x["proporcion_mora_mayor_90d"], 0.05)
        self.assertFalse(x["es_pd_individual"])
        self.assertEqual(x["indicador_cartera_vencida_fuente"], "4.2")

    def test_future_rejected(self):
        self.assertIsNone(m.normalized(record(), date(2025, 1, 1)))

    def test_bad_reconciliation(self):
        with self.assertRaises(ValueError):
            m.normalized(record(total_creditos="101"), date(2025, 1, 31))

    def test_duplicate_grain(self):
        with self.assertRaises(ValueError):
            m.build([record(), record()], date(2025, 1, 31))

    def test_phase_is_part_of_unique_grain(self):
        result = m.build([record(), record(epoca_cartera="ESTUDIOS")], date(2025, 1, 31))
        self.assertEqual(len(result), 2)

    def test_fractional_count(self):
        with self.assertRaises(ValueError):
            m.normalized(record(cantidad_creditos_al_dia="80.5"), date(2025, 1, 31))


if __name__ == "__main__":
    unittest.main()
