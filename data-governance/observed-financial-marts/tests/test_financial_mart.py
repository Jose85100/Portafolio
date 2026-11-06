import importlib.util
import pathlib
import unittest
from datetime import date

p = pathlib.Path(__file__).resolve().parents[1] / "src" / "financial_mart.py"
spec = importlib.util.spec_from_file_location("financial_mart", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def sfc(y, q, credit=100):
    return {"fecha_corte": f"{y}-{q:02d}-30",
            "depositos_corriente": "20", "depositos_ahorro": "40",
            "cdt": "40", "cartera_creditos": str(credit),
            "creditos_vivienda": "10", "numero_oficinas": "1"}


def rate(month, value="10"):
    return {"mes": month, "dtf_promedio": "8", "ibr_promedio": value,
            "tib_promedio": "11", "observaciones_dtf": "3",
            "observaciones_ibr": "4" if value else "0", "observaciones_tib": "2"}


class RealDataContractTests(unittest.TestCase):
    def test_mart_growth_and_funding(self):
        rows = m.compute([sfc(2024, 6), sfc(2025, 6, 120)],
                         [rate("2024-03"), rate("2025-03")])
        self.assertEqual(len(rows), 2)
        self.assertAlmostEqual(rows[-1]["crecimiento_cartera_yoy_pct"], 20)
        self.assertAlmostEqual(rows[-1]["cartera_sobre_depositos"], 1.2)
        self.assertEqual(rows[-1]["mes_ibr_rezagado"], "2025-03")
        self.assertFalse(rows[-1]["is_obligor_pd"])

    def test_missing_rates_no_synthetic_fill(self):
        row = m.compute([sfc(2025, 6)], [rate("2024-02")])[0]
        self.assertIsNone(row["ibr_rezagado_pct"])

    def test_duplicate_quarter(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            m.compute([sfc(2025, 6), sfc(2025, 6)], [])

    def test_rate_count_reconciliation(self):
        with self.assertRaisesRegex(ValueError, "inconsistent"):
            m.compute([sfc(2025, 6)], [{**rate("2025-03", ""), "observaciones_ibr": "4"}])

    def test_nonfinite_and_invalid_denominator(self):
        with self.assertRaises(ValueError):
            m.compute([sfc(2025, 6, float("nan"))], [])
        row = sfc(2025, 6)
        for key in ("depositos_corriente", "depositos_ahorro", "cdt"):
            row[key] = "0"
        with self.assertRaisesRegex(ValueError, "denominator"):
            m.compute([row], [])


if __name__ == "__main__":
    unittest.main()
