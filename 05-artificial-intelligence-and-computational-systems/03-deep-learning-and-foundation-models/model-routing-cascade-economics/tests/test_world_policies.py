import unittest
import numpy as np
import _path  # noqa: F401
from routerlab.world import World, sigmoid, logit, DEFAULT_TIERS
from routerlab import policies as P


class TestWorld(unittest.TestCase):
    def setUp(self): self.w = World(); self.df = self.w.sample(60000, np.random.default_rng(0))

    def test_columnas_y_determinismo(self):
        a = self.w.sample(100, np.random.default_rng(1)); b = self.w.sample(100, np.random.default_rng(1)); self.assertTrue(a.equals(b))
        for t in self.w.tiers: self.assertTrue({f"p_{t.name}", f"correct_{t.name}", f"conf_{t.name}"} <= set(a.columns))

    def test_la_tasa_de_acierto_coincide_con_la_probabilidad(self):
        for t in self.w.tiers: self.assertAlmostEqual(self.df[f"correct_{t.name}"].mean(), self.df[f"p_{t.name}"].mean(), delta=0.006)

    def test_niveles_mas_hábiles_aciertan_mas(self):
        m = [self.df[f"correct_{t.name}"].mean() for t in self.w.tiers]; self.assertTrue(m[0] < m[1] < m[2])

    def test_resultados_correlacionados_pero_no_anidados(self):
        c = self.df[["correct_small", "correct_large"]].corr().iloc[0, 1]; self.assertGreater(c, 0.15)
        self.assertGreater(((self.df.correct_small == 1) & (self.df.correct_large == 0)).mean(), 0.003)              # la pequena a veces acierta cuando la grande falla

    def test_atributos_informativos_de_la_dificultad(self):
        self.assertGreater(np.corrcoef(self.df.f0, self.df.difficulty)[0, 1], 0.5); self.assertLess(abs(np.corrcoef(self.df.f3, self.df.difficulty)[0, 1]), 0.02)

    def test_confianza_calibrada(self):
        c = self.df.conf_small.values; y = self.df.correct_small.values
        for lo, hi in ((0.0, 0.2), (0.4, 0.6), (0.8, 1.0)): m = (c >= lo) & (c < hi + 1e-9); self.assertAlmostEqual(y[m].mean(), c[m].mean(), delta=0.05)

    def test_sobreconfianza_es_mas_extrema(self):
        o = World(conf_kind="overconfident").sample(60000, np.random.default_rng(0)); self.assertGreater(o.conf_small.std(), self.df.conf_small.std())
        m = (o.conf_small >= 0.8).values; self.assertGreater(o.conf_small[m].mean() - o.correct_small[m].mean(), 0.05)         # dice mas de lo que acierta
        with self.assertRaises(ValueError): World(conf_kind="x")


class TestPolicies(unittest.TestCase):
    def setUp(self): self.w = World(); self.df = self.w.sample(40000, np.random.default_rng(1))

    def test_siempre_un_nivel(self):
        for t in self.w.tiers:
            r = P.always_tier(self.df, self.w, t.name); e = P.evaluate(r); self.assertEqual(e["mean_cost"], t.cost_per_call); self.assertEqual(e["escalation_rate"], 0.0); self.assertAlmostEqual(e["quality"], self.df[f"correct_{t.name}"].mean())

    def test_contabilidad_de_la_cascada_a_mano(self):
        df = self.df.iloc[:6].copy(); df["conf_small"] = [0.9, 0.2, 0.9, 0.2, 0.9, 0.2]; df["conf_medium"] = [0.9, 0.9, 0.2, 0.2, 0.9, 0.9]
        r = P.cascade(df, self.w, [0.5, 0.5]); esperado = np.array([1, 7, 1, 37, 1, 7.0]); self.assertTrue(np.array_equal(r["cost"], esperado)); self.assertTrue(np.array_equal(r["calls"], [1, 2, 1, 3, 1, 2]))
        self.assertEqual(r["latency"][3], 200 + 700 + 2200)

    def test_umbral_cero_es_el_nivel_pequeno_y_umbral_alto_es_el_grande_con_todo_el_costo(self):
        a = P.evaluate(P.cascade(self.df, self.w, [0.0, 0.0])); self.assertEqual(a["mean_cost"], 1.0); self.assertAlmostEqual(a["quality"], self.df.correct_small.mean())
        b = P.cascade(self.df, self.w, [2.0, 2.0]); self.assertEqual(P.evaluate(b)["mean_cost"], 37.0); self.assertAlmostEqual(P.evaluate(b)["quality"], self.df.correct_large.mean())

    def test_la_cascada_cuesta_mas_que_su_ultimo_nivel_solo_si_escala_siempre(self):
        r = P.cascade(self.df, self.w, [0.7, 0.7]); e = P.evaluate(r); self.assertTrue(1.0 <= e["mean_cost"] <= 37.0); self.assertTrue(np.all(r["cost"] >= 1.0))

    def test_cascada_mas_exigente_cuesta_mas_y_acierta_mas(self):
        q = []; c = []
        for th in (0.3, 0.5, 0.7, 0.9): e = P.evaluate(P.cascade(self.df, self.w, [th, th])); q.append(e["quality"]); c.append(e["mean_cost"])
        self.assertTrue(np.all(np.diff(c) > 0) and np.all(np.diff(q) > 0))

    def test_oraculo_domina_consulta_por_consulta(self):
        """Por consulta: el oraculo acierta siempre que la politica acierta, y cuando la politica acierta su costo no supera al de la politica."""
        o = P.oracle_router(self.df, self.w)
        pols = [P.always_tier(self.df, self.w, t.name) for t in self.w.tiers] + [P.cascade(self.df, self.w, [th, th]) for th in (0.3, 0.6, 0.9)]
        for r in pols:
            self.assertTrue(np.all(o["correct"] >= r["correct"])); acierta = r["correct"] == 1; self.assertTrue(np.all(o["cost"][acierta] <= r["cost"][acierta] + 1e-12))
        self.assertGreaterEqual(P.evaluate(o)["quality"], max(P.evaluate(r)["quality"] for r in pols))

    def test_oraculo_cuenta_un_solo_costo_por_consulta(self):
        r = P.oracle_router(self.df, self.w); self.assertTrue(set(np.unique(r["cost"])) <= {1.0, 6.0, 30.0})

    def test_regresion_logistica_recupera_coeficientes(self):
        rg = np.random.default_rng(0); X = rg.standard_normal((20000, 2)); p = 1 / (1 + np.exp(-(0.5 + 1.2 * X[:, 0] - 0.8 * X[:, 1]))); y = (rg.random(20000) < p).astype(int)
        m = P.LogisticReg(l2=0.0).fit(X, y); self.assertTrue(np.allclose(m.w, [0.5, 1.2, -0.8], atol=0.07))

    def test_enrutador_aprendido_mejor_que_azar_y_monotono_en_tau(self):
        tr = self.w.sample(20000, np.random.default_rng(2)); res = []
        for tau in (0.2, 0.4, 0.6, 0.8): r, ph = P.learned_router(tr, self.df, self.w, tau); res.append(P.evaluate(r))
        self.assertTrue(np.all(np.diff([x["mean_cost"] for x in res]) > 0)); r2, _ = P.learned_router(tr, self.df, self.w, 0.5)
        frac = (r2["cost"] == 1.0).mean(); azar_q = frac * self.df.correct_small.mean() + (1 - frac) * self.df.correct_large.mean(); self.assertGreater(P.evaluate(r2)["quality"], azar_q + 0.01)

    def test_frontera_de_pareto_contra_fuerza_bruta(self):
        rg = np.random.default_rng(3)
        for _ in range(100):
            pts = [tuple(x) for x in rg.random((12, 2))]; f = set(P.pareto_frontier(pts))
            bruta = {i for i, (c, q) in enumerate(pts) if not any(c2 <= c and q2 >= q and (c2 < c or q2 > q) for j, (c2, q2) in enumerate(pts) if j != i)}; self.assertEqual(f, bruta)

    def test_frontera_casos_simples(self):
        self.assertEqual(P.pareto_frontier([(1, 0.5), (2, 0.4), (3, 0.9)]), [0, 2]); self.assertEqual(P.pareto_frontier([(1, 0.5), (1, 0.5)]), [0, 1])


if __name__ == "__main__":
    unittest.main()
