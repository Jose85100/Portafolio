"""Pruebas de invariantes de los proyectos insignia.

    python3 -m unittest discover -s 00-proyectos-insignia/tests -v
"""
import sys
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
for sub in ("", "01-riesgo-estres-consumo", "02-validacion-modelo-satelite", "03-caso-negocio-credito-digital",
            "04-usura-racionamiento-credito"):
    sys.path.insert(0, str(RAIZ / sub))

import caso as K  # noqa: E402
import estres as E  # noqa: E402
import usura_efectos as U  # noqa: E402
import validacion as V  # noqa: E402
from comun import cartera, expit, logit, macro  # noqa: E402


class CapaDeDatos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = cartera()

    def test_reconciliacion(self):
        self.assertGreater(self.c["reconcilia"].mean(), 0.99)

    def test_mora90_no_supera_mora30(self):
        self.assertTrue((self.c["mora90"] <= self.c["mora30"] + 1).all())

    def test_una_fila_por_entidad_producto_mes(self):
        self.assertFalse(self.c.duplicated(["mes", "codigo_entidad", "unicap"]).any())

    def test_macro_tiene_series_clave(self):
        m = macro()
        for v in ("tpm", "inflacion", "desempleo_12m", "ise_crec"):
            self.assertGreater(m[v].notna().sum(), 100, v)

    def test_logit_inverso(self):
        p = pd.Series([0.01, 0.2, 0.7])
        np.testing.assert_allclose(expit(logit(p)), p)


class Estres(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = E.series_consumo()
        cls.p = E.por_producto()
        cls.d = E.base_modelo(cls.s)

    def test_shift_share_cuadra(self):
        ss = E.shift_share(self.p, "2022-04", "2024-01")
        a, b = self.p.xs("2022-04"), self.p.xs("2024-01")
        total = b["mora90"].sum() / b["saldo"].sum() - a["mora90"].sum() / a["saldo"].sum()
        self.assertAlmostEqual(ss["total"].sum(), total, places=4)

    def test_seleccion_compara_misma_muestra_y_signos(self):
        t = E.seleccionar_rezagos(self.d)
        self.assertEqual(t["n"].nunique(), 1)
        rez = E.rezagos_elegidos(t)
        sat = E.ajustar(self.d, rez)
        self.assertTrue((sat.params[["tpm", "inflacion", "crec"]] > 0).all())

    def test_escenarios_ordenados(self):
        rez = E.rezagos_elegidos(E.seleccionar_rezagos(self.d))
        sat = E.ajustar(self.d, rez)
        P = {k: E.proyectar(sat, self.d, v) for k, v in E.trayectorias_macro(self.d).items()}
        self.assertEqual(len(P["Base"]), 24)
        self.assertLessEqual(P["Base"].max(), P["Adverso"].max())
        self.assertLessEqual(P["Adverso"].max(), P["Severo"].max())

    def test_semaforo_anonimo(self):
        sem = E.semaforo_entidades()
        self.assertNotIn("entidad", sem.columns)
        self.assertTrue(sem["codigo"].str.match(r"E\d{2}").all())


class Validacion(unittest.TestCase):
    def test_replica_exacta(self):
        self.assertLess(V.replicar_icv()["dif_pb"].abs().max(), 0.01)

    def test_diebold_mariano_simetrico(self):
        rng = np.random.default_rng(0)
        a, b = rng.normal(size=60), rng.normal(size=60)
        self.assertAlmostEqual(V.diebold_mariano(a, b, 3)[0], -V.diebold_mariano(b, a, 3)[0])

    def test_remediado_converge_a_relacion_macro(self):
        d = E.base_modelo()
        rez = E.rezagos_elegidos(E.seleccionar_rezagos(d))
        m = V.ajustar_remediado(d, rez)
        self.assertLess(abs(m["phi"]), 1)


class Caso(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pr = K.precios()
        cls.rg = K.riesgo_producto()
        cls.uh = K.usura_vigente()[1]

    def test_mediana_ponderada(self):
        self.assertEqual(K.mediana_ponderada(np.array([1.0, 2.0, 3.0]), np.array([1.0, 1.0, 10.0])), 3.0)

    def test_identidad_resultados(self):
        u = K.economia_unitaria("Tarjeta de crédito", self.pr, self.rg, 12.25, self.uh, K.Supuestos())
        self.assertAlmostEqual(u["utilidad_antes_imp"],
                               u["rendimiento"] + u["comisiones"] - u["fondeo"] - u["perdida"] - u["opex"] - u["cac"])

    def test_precio_respeta_techo(self):
        for prod in K.PRODUCTOS:
            self.assertLessEqual(K.precio_entrante(self.pr, prod, self.uh, K.Supuestos()), self.uh)

    def test_fondeo_mas_caro_baja_roe(self):
        s = K.Supuestos()
        a = K.economia_unitaria("Libre inversión", self.pr, self.rg, 12.25, self.uh, s)["roe"]
        b = K.economia_unitaria("Libre inversión", self.pr, self.rg, 12.25, self.uh, replace(s, spread_fondeo_pp=5))["roe"]
        self.assertLess(b, a)

    def test_plan_cumple_capital(self):
        pl = K.plan("Tarjeta de crédito", self.pr, self.rg, 12.25, self.uh, K.Supuestos())
        self.assertTrue((pl["patrimonio"] >= pl["capital_requerido"] - 1).all())


class Usura(unittest.TestCase):
    def test_amontonamiento_nulo_en_uniforme(self):
        rng = np.random.default_rng(1)
        p = pd.DataFrame({"producto": "x", "ratio": rng.uniform(0.8, 1.0, 200_000)})
        self.assertAlmostEqual(U.amontonamiento(p, "x", grado=1)["razon_masa"], 1.0, delta=0.03)

    def test_tratamiento_definido_fuera_de_la_ventana(self):
        """Una celda que solo toca el techo en las semanas -4..-1 no debe quedar tratada (regla habitual)."""
        semanas = pd.date_range("2020-01-03", periods=30, freq="7D")
        ev = pd.DataFrame({"desde": [semanas[15]], "techo_previo": [30.0], "techo_nuevo": [29.0], "cambio_pp": [-1.0]})
        filas = []
        for i, s in enumerate(semanas):
            rel = i - 15
            filas.append({"semana": s, "producto": "Tarjeta personas", "celda": "a", "tasa_ea": 29.9 if -4 <= rel <= -1 else 25.0,
                          "ratio": (29.9 if -4 <= rel <= -1 else 25.0) / 30, "monto": 1.0, "n_creditos": 1.0})
            filas.append({"semana": s, "producto": "Tarjeta personas", "celda": "b", "tasa_ea": 29.8, "ratio": 29.8 / 30,
                          "monto": 1.0, "n_creditos": 1.0})
        st = U.apilar(pd.DataFrame(filas), ev, ["Tarjeta personas"])
        trat = st.groupby("celda")["tratada"].first()
        self.assertEqual(trat["a"], 0)
        self.assertEqual(trat["b"], 1)


if __name__ == "__main__":
    unittest.main()
