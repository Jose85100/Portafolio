"""Pruebas de invariantes matemáticos del modelo de crédito."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "03-financial-risk" / "credit-portfolio-strategy" / "copula-gaussiana-perdidas" / "modelo_avanzado.py"
spec = importlib.util.spec_from_file_location("modelo_credito_avanzado", FILE)
mod = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class PruebasCreditoAvanzado(unittest.TestCase):
    def test_pd_cero_y_uno(self):
        l = mod.simular_perdidas([0, 1], [1, 0.5], [100, 200], [0, 0.5],
                                 simulaciones=200, semilla=1)
        np.testing.assert_array_equal(l, np.full(200, 100.0))

    def test_reproducibilidad(self):
        kwargs = dict(pd=[0.1, 0.3], lgd=[0.5, 0.8], ead=[100, 200],
                      rho=[0.1, 0.2], simulaciones=1000, semilla=5)
        np.testing.assert_array_equal(mod.simular_perdidas(**kwargs),
                                      mod.simular_perdidas(**kwargs))

    def test_media_analitica(self):
        p, g, e = [0.2], [0.5], [100.0]
        l = mod.simular_perdidas(p, g, e, [0.3], simulaciones=60_000)
        m = mod.metricas(l, p, g, e, confianza=0.95)
        self.assertAlmostEqual(m.perdida_esperada_analitica, 10.0)
        self.assertLess(abs(m.perdida_esperada_montecarlo - 10),
                        5 * m.error_estandar_media)

    def test_es_empirico_discreto(self):
        m = mod.metricas([0, 0, 10, 10], [0.5], [1], [10], confianza=0.75)
        self.assertEqual(m.expected_shortfall, 10.0)
        self.assertEqual(m.var, 10.0)

    def test_es_fraccionario(self):
        m = mod.metricas([0, 0, 10, 20], [0.5], [1], [10], confianza=0.625)
        self.assertAlmostEqual(m.expected_shortfall, (20 + 0.5 * 10) / 1.5)

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            mod.simular_perdidas([0.1], [0.5], [100], [1.2])


if __name__ == "__main__":
    unittest.main()
