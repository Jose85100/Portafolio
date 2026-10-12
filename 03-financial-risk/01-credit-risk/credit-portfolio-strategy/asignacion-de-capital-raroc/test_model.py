"""Pruebas de invariantes económicos del ejemplo de asignación."""

import importlib.util
from pathlib import Path
import sys
import unittest

import numpy as np

MODULE_PATH = Path(__file__).with_name("main.py")
spec = importlib.util.spec_from_file_location("asignacion_raroc", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

asignar_max_raroc = module.asignar_max_raroc
asignar_max_utilidad = module.asignar_max_utilidad
metricas = module.metricas
segmentos_sinteticos = module.segmentos_sinteticos


class TestAsignacionRAROC(unittest.TestCase):
    def setUp(self):
        self.segmentos, self.k = segmentos_sinteticos(), 0.085

    def test_soluciones_respetan_restricciones(self):
        for pesos in (asignar_max_raroc(self.segmentos, self.k), asignar_max_utilidad(self.segmentos, self.k)):
            self.assertAlmostEqual(float(pesos.sum()), 1.0, places=9)
            self.assertTrue(np.all(pesos >= -1e-10))
            self.assertTrue(np.all(pesos <= self.segmentos["tope"].to_numpy() + 1e-9))
            self.assertLessEqual(metricas(self.segmentos, pesos)["capital"], self.k + 1e-9)

    def test_objetivos_se_distinguen(self):
        m_raroc = metricas(self.segmentos, asignar_max_raroc(self.segmentos, self.k))
        m_utilidad = metricas(self.segmentos, asignar_max_utilidad(self.segmentos, self.k))
        self.assertGreaterEqual(m_raroc["raroc"], m_utilidad["raroc"] - 1e-9)
        self.assertGreaterEqual(m_utilidad["utilidad"], m_raroc["utilidad"] - 1e-9)


if __name__ == "__main__":
    unittest.main()
