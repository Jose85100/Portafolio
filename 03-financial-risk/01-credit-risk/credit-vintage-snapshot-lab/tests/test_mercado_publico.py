import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mercado_publico as mp  # noqa: E402


def _raw_tarjetas():
    filas = []
    for fecha in ("2025-01-31", "2025-02-28"):
        for uca in ("1", "2", "6"):  # 6 = débito, debe excluirse
            for desc, nat, jur, total in [
                ("Número total de tarjetas de crédito vigentes  a la fecha de corte", 90, 10, 100),
                ("Saldo de la cartera por tarjeta de crédito", 0, 0, 600),
                ("Total cupo de crédito no utilizado por todos los tarjetahabientes", 0, 0, 400),
                ("Monto de las transacciones por avances con tarjeta de crédito a nivel nacional", 0, 0, 20),
                ("Monto de las transacciones por compras con tarjeta de crédito a nivel nacional", 0, 0, 80),
            ]:
                filas.append(dict(tipoentidad=1, codigoentidad=7, nombreentidad="BANCOLOMBIA S.A.", fechacorte=fecha,
                                  cod_uca=uca, descripcion=desc, persona_natural=nat, persona_juridica=jur,
                                  total_tarjetas=total))
    return pd.DataFrame(filas)


class LimpiezaTest(unittest.TestCase):
    def test_tarjetas_suma_franquicias_de_credito_y_separa_persona(self):
        t = mp.tidy_tarjetas(_raw_tarjetas())
        self.assertEqual(len(t), 2)
        fila = t.iloc[0]
        self.assertEqual(fila["tarjetas_vigentes"], 200)          # dos franquicias de crédito, sin débito
        self.assertEqual(fila["tarjetas_vigentes_natural"], 180)
        self.assertEqual(fila["tarjetas_vigentes_juridica"], 20)
        self.assertEqual(fila["entidad"], "Bancolombia")
        ind = mp.indicadores_tarjeta(t).iloc[0]
        self.assertAlmostEqual(ind["utilizacion"], 1200 / 2000)
        self.assertAlmostEqual(ind["peso_avances_monto"], 40 / 200)
        self.assertAlmostEqual(ind["participacion_juridica"], 0.1)

    def test_mora_por_altura_y_calificacion(self):
        c = pd.DataFrame([dict(tipo_entidad=1, codigo_entidad=7, entidad="X", fecha=pd.Timestamp("2025-01-31"),
                               producto="TARJETAS DE CREDITO", segmento="total", saldo=1000, vigente=900,
                               mora_30_60=40, mora_60_90=20, mora_90_180=30, mora_180_mas=10, clientes_mora=5,
                               saldo_A=850, saldo_B=50, saldo_C=40, saldo_D=30, saldo_E=30)])
        r = mp.indicadores_mora(c).iloc[0]
        self.assertAlmostEqual(r["icv30"], 0.10)
        self.assertAlmostEqual(r["icv60"], 0.06)
        self.assertAlmostEqual(r["icv90"], 0.04)
        self.assertAlmostEqual(r["calidad_cde"], 0.10)
        self.assertAlmostEqual(r["descuadre"], 0.0)

    def test_tibc_texto_con_porcentaje_y_usura(self):
        raw = pd.DataFrame({"resolucion": [1, 2], "interes_bancario_corriente": ["20,00%", "18.5%"],
                            "vigencia_desde": ["2025-01-01", "2025-02-01"], "vigencia_hasta": ["2025-01-31", "2025-02-28"],
                            "modalidad": ["CONSUMO Y ORDINARIO "] * 2})
        t = mp.tidy_tibc(raw)
        self.assertAlmostEqual(t["usura_ea"].iloc[0], 0.30)
        u = mp.usura_mensual(t)
        self.assertAlmostEqual(u.loc["2025-02-28"], 1.5 * 0.185)

    def test_nombre_corto(self):
        self.assertEqual(mp.nombre_corto("BANCO DAVIVIENDA S.A."), "Davivienda")
        self.assertTrue(np.isnan(mp.nombre_corto(np.nan)))


class IndicadoresTest(unittest.TestCase):
    def test_anualizar_exige_doce_meses_consecutivos(self):
        fechas = pd.date_range("2024-01-31", periods=14, freq="ME")
        df = pd.DataFrame({"e": 1, "fecha": fechas, "castigo": 1.0, "saldo": 100.0})
        r = mp.anualizar_flujo(df, "castigo", "saldo", ["e"])
        self.assertTrue(r.iloc[:11].isna().all())
        self.assertAlmostEqual(r.iloc[11], 0.12)
        hueco = df.drop(index=5).reset_index(drop=True)
        self.assertTrue(mp.anualizar_flujo(hueco, "castigo", "saldo", ["e"]).iloc[:12].isna().all())

    def test_hhi_y_percentil(self):
        self.assertAlmostEqual(mp.hhi(pd.Series([1, 1, 1, 1])), 2500)
        self.assertAlmostEqual(mp.hhi(pd.Series([5])), 10000)
        self.assertAlmostEqual(mp.percentil_en_mercado(2.5, pd.Series([1, 2, 3, 4])), 0.5)
        self.assertAlmostEqual(mp.percentil_en_mercado(2, pd.Series([1, 2, 3]), pd.Series([1, 2, 1])), 0.5)

    def test_mora_estacionaria(self):
        # Todo entra a mora en MOB 1 y nunca sale: el stock es la tasa de entrada.
        self.assertAlmostEqual(mp.mora_stock_estacionaria(np.full(24, 0.05), roll_off=0.0), 0.05)
        # Con salida del balance el stock es menor que la entrada acumulada.
        curva = np.linspace(0.01, 0.12, 24)
        sin_salida = mp.mora_stock_estacionaria(curva, roll_off=0.0)
        con_salida = mp.mora_stock_estacionaria(curva, roll_off=0.15)
        self.assertLess(con_salida, sin_salida)
        # Crecer pesa más las cosechas jóvenes: baja el stock si la mora sube con la edad...
        lenta = mp.perfil_mora_por_edad(curva, 0.0)
        self.assertTrue(np.all(np.diff(lenta) >= 0))
        self.assertLess(mp.mora_stock_estacionaria(curva, 0.0, crecimiento_mensual=0.03), sin_salida)
        # ...y lo sube si la mora entra temprano y sale rápido (perfil decreciente con la edad).
        temprana = np.r_[0.08, np.full(23, 0.08)]
        self.assertTrue(np.all(np.diff(mp.perfil_mora_por_edad(temprana, 0.3)) <= 0))
        self.assertGreater(mp.mora_stock_estacionaria(temprana, 0.3, 0.03), mp.mora_stock_estacionaria(temprana, 0.3))


if __name__ == "__main__":
    unittest.main()
