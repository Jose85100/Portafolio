import importlib.util
import pathlib
import unittest

path = pathlib.Path(__file__).resolve().parents[1] / "src" / "portfolio_signals.py"
spec = importlib.util.spec_from_file_location("portfolio_signals", path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def row(date, phase, total, late):
    return {"fecha_corte": date, "epoca_cartera": phase,
            "creditos_total": str(total), "creditos_mora_mayor_90d": str(late),
            "evidencia": "OBSERVADO_AGREGADO"}


class SignalTests(unittest.TestCase):
    def test_weight_by_counts_not_department_means(self):
        result = m.signals([row("2025-01-01", "AMORTIZACION", 100, 10),
                            row("2025-01-01", "AMORTIZACION", 10, 8)])
        overall = next(x for x in result if x["epoca_cartera"] == "ALL_PHASES")
        self.assertAlmostEqual(overall["share_creditos_mora_mayor_90d"], 18 / 110)

    def test_phases_separate(self):
        result = m.signals([row("2025-01-01", "AMORTIZACION", 100, 10),
                            row("2025-01-01", "ESTUDIOS", 50, 1)])
        self.assertEqual(len(result), 3)
        self.assertEqual(next(x for x in result if x["epoca_cartera"] == "ALL_PHASES")["creditos_total"], 150)

    def test_synthetic_rejected(self):
        x = row("2025-01-01", "ESTUDIOS", 100, 10)
        x["evidencia"] = "SYNTHETIC"
        with self.assertRaises(ValueError):
            m.signals([x])

    def test_invalid_counts_rejected(self):
        with self.assertRaises(ValueError):
            m.signals([row("2025-01-01", "ESTUDIOS", 10, 12)])


if __name__ == "__main__":
    unittest.main()
