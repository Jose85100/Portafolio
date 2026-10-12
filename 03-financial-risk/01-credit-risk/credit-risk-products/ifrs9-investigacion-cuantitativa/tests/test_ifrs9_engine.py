import sys
from pathlib import Path
import unittest
import numpy as np

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
from src.ifrs9_engine import cartera_sintetica, ecl_componentes, ponderar_escenarios, stage


class TestIFRS9Laboratory(unittest.TestCase):
    def setUp(self): self.cartera = cartera_sintetica(200, 7)

    def test_stage_3_requires_90_days_past_due(self):
        resultado = stage(self.cartera.pd_12m, self.cartera.pd_origen, self.cartera.dpd)
        self.assertTrue((resultado[self.cartera.dpd >= 90] == 3).all())

    def test_adverse_ecl_exceeds_base(self):
        base = ecl_componentes(self.cartera, "base").ecl.sum()
        adverso = ecl_componentes(self.cartera, "adverso").ecl.sum()
        self.assertGreater(adverso, base)

    def test_weights_and_ecl_are_valid(self):
        tabla = ponderar_escenarios(self.cartera, {"base": .6, "adverso": .3, "severo": .1})
        self.assertTrue(np.isfinite(tabla.ecl_ponderada).all())
        self.assertTrue((tabla.ecl_ponderada >= 0).all())
