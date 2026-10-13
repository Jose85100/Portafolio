import unittest
import numpy as np
from scipy import stats as st
import _path  # noqa: F401
from evalkit import stats as S


class TestIntervalos(unittest.TestCase):
    def test_wilson_valores_conocidos(self):
        lo, hi = S.wilson_ci(8, 10); self.assertAlmostEqual(lo, 0.4902, places=3); self.assertAlmostEqual(hi, 0.9433, places=3)
        lo, hi = S.wilson_ci(0, 20); self.assertEqual(round(lo, 6), 0.0); self.assertAlmostEqual(hi, 0.1611, places=3)

    def test_clopper_pearson_valor_conocido_y_extremos(self):
        lo, hi = S.clopper_pearson_ci(8, 10); self.assertAlmostEqual(lo, 0.4439, places=3); self.assertAlmostEqual(hi, 0.9748, places=3)
        self.assertEqual(S.clopper_pearson_ci(0, 10)[0], 0.0); self.assertEqual(S.clopper_pearson_ci(10, 10)[1], 1.0)

    def test_orden_de_anchos_y_contencion(self):
        for k, n in [(3, 20), (50, 100), (1, 30)]:
            w, c = S.wilson_ci(k, n), S.clopper_pearson_ci(k, n); self.assertGreaterEqual(c[1] - c[0], w[1] - w[0] - 1e-9); self.assertTrue(w[0] <= k / n <= w[1])

    def test_wald_degenera_en_extremos(self):
        self.assertEqual(S.wald_ci(0, 20), (0.0, 0.0)); self.assertGreater(S.wilson_ci(0, 20)[1], 0.1)

    def test_cobertura_clopper_pearson_nunca_menor_a_nominal(self):
        for p in (0.02, 0.1, 0.5):
            n = 40; ks = np.arange(n + 1); pm = st.binom.pmf(ks, n, p)
            cub = sum(pm[k] for k in ks if S.clopper_pearson_ci(k, n)[0] <= p <= S.clopper_pearson_ci(k, n)[1]); self.assertGreaterEqual(cub, 0.95 - 1e-9)


class TestPareadas(unittest.TestCase):
    def test_mcnemar_igual_a_binomtest(self):
        for b, c in [(10, 3), (5, 5), (0, 8), (20, 12)]:
            self.assertAlmostEqual(S.mcnemar_exact(b, c), st.binomtest(b, b + c, 0.5).pvalue, places=10)
        self.assertEqual(S.mcnemar_exact(0, 0), 1.0)

    def test_mcnemar_calibrada_bajo_h0(self):
        rg = np.random.default_rng(0); rech = 0
        for _ in range(3000):
            b = rg.binomial(30, 0.5); rech += S.mcnemar_exact(b, 30 - b) < 0.05
        self.assertLess(rech / 3000, 0.05 + 0.01)          # la prueba exacta es conservadora

    def test_tamano_de_muestra_pareado_da_la_potencia_pedida(self):
        p10, p01 = 0.15, 0.08; n = S.n_paired_binary(p10, p01); rg = np.random.default_rng(1); rech = 0
        for _ in range(1500):
            cnt = rg.multinomial(n, [p10, p01, 1 - p10 - p01]); rech += S.mcnemar_exact(cnt[0], cnt[1]) < 0.05
        self.assertTrue(0.74 < rech / 1500 < 0.90)

    def test_dos_proporciones_tamano_y_potencia(self):
        n = S.n_two_prop(0.6, 0.7); rg = np.random.default_rng(2); rech = 0
        for _ in range(1500): rech += S.two_prop_z(rg.binomial(n, 0.6), n, rg.binomial(n, 0.7), n) < 0.05
        self.assertTrue(0.74 < rech / 1500 < 0.88)

    def test_pareado_necesita_menos_muestra_si_hay_correlacion(self):
        # mismas tasas marginales (0.6 vs 0.7) con discordancia pequena => mucho menos muestra pareada que independiente
        self.assertLess(S.n_paired_binary(0.12, 0.02), S.n_two_prop(0.6, 0.7))

    def test_ic_por_grupos_es_mas_ancho_con_correlacion_dentro_del_grupo(self):
        rg = np.random.default_rng(3); g = np.repeat(np.arange(50), 10); u = rg.standard_normal(50)[g]; x = u + 0.3 * rg.standard_normal(500)
        m, lo, hi = S.cluster_mean_ci(x, g); naive = 1.96 * x.std(ddof=1) / np.sqrt(500); self.assertGreater(hi - lo, 2 * naive); self.assertAlmostEqual(m, x.mean(), places=10)


class TestAcuerdo(unittest.TestCase):
    def test_kappa_de_cohen_ejemplo_clasico(self):
        a = np.r_[np.ones(20), np.ones(5), np.zeros(10), np.zeros(15)]; b = np.r_[np.ones(20), np.zeros(5), np.ones(10), np.zeros(15)]
        self.assertAlmostEqual(S.cohen_kappa(a, b), 0.4, places=10)

    def test_kappa_perfecto_y_azar(self):
        x = np.random.default_rng(0).integers(0, 2, 1000); self.assertEqual(S.cohen_kappa(x, x), 1.0)
        self.assertAlmostEqual(S.cohen_kappa(x, np.random.default_rng(1).integers(0, 2, 1000)), 0.0, delta=0.08)

    def test_paradoja_del_kappa(self):
        a = np.r_[np.ones(90), np.zeros(10)]; b = np.r_[np.ones(85), np.zeros(5), np.ones(5), np.zeros(5)]
        self.assertGreaterEqual(np.mean(a == b), 0.9); self.assertAlmostEqual(S.cohen_kappa(a, b), (0.9 - 0.82) / 0.18, places=10)       # acuerdo alto, kappa moderado por prevalencia

    def test_fleiss_ejemplo_de_wikipedia(self):
        c = np.array([[0, 0, 0, 0, 14], [0, 2, 6, 4, 2], [0, 0, 3, 5, 6], [0, 3, 9, 2, 0], [2, 2, 8, 1, 1], [7, 7, 0, 0, 0], [3, 2, 6, 3, 0], [2, 5, 3, 2, 2], [6, 5, 2, 1, 0], [0, 2, 2, 3, 7]])
        self.assertAlmostEqual(S.fleiss_kappa(c), 0.210, places=3)

    def test_krippendorff_acuerdo_perfecto_y_a_mano(self):
        R = np.array([[1, 0, 1, 0], [1, 0, 1, 0], [1, 0, 1, 0.]]); self.assertAlmostEqual(S.krippendorff_alpha_nominal(R), 1.0)
        R2 = np.array([[1, 1, 0, 0], [1, 0, 0, 1.]]); self.assertAlmostEqual(S.krippendorff_alpha_nominal(R2), 0.0, delta=0.34)

    def test_krippendorff_con_faltantes_y_cercano_a_kappa(self):
        rg = np.random.default_rng(0); t = rg.integers(0, 2, 400); a = np.where(rg.random(400) < .85, t, 1 - t); b = np.where(rg.random(400) < .85, t, 1 - t)
        k = S.cohen_kappa(a, b); al = S.krippendorff_alpha_nominal(np.vstack([a, b]).astype(float)); self.assertAlmostEqual(k, al, delta=0.03)
        R = np.vstack([a, b]).astype(float); R[0, :50] = np.nan; self.assertTrue(np.isfinite(S.krippendorff_alpha_nominal(R)))


class TestCorreccionJuez(unittest.TestCase):
    def test_rogan_gladen_invierte_el_sesgo(self):
        p, tpr, tnr = 0.4, 0.9, 0.85; p_obs = p * tpr + (1 - p) * (1 - tnr); self.assertAlmostEqual(S.rogan_gladen(p_obs, tpr, tnr), p, places=10)
        self.assertEqual(S.rogan_gladen(0.0, 0.9, 0.85), 0.0)

    def test_ppi_es_insesgado_y_cubre_aunque_el_juez_sea_sesgado(self):
        rg = np.random.default_rng(0); p = 0.55; cub = 0; est = []
        for _ in range(1500):
            y = (rg.random(3000) < p).astype(int); j = np.where(y == 1, rg.random(3000) < 0.95, rg.random(3000) < 0.30).astype(int)
            lab = np.arange(200); th, lo, hi = S.ppi_mean(j[200:], j[lab], y[lab]); est.append(th); cub += lo <= p <= hi
        self.assertAlmostEqual(np.mean(est), p, delta=0.004); self.assertTrue(0.93 < cub / 1500 < 0.97)
        # el juez solo estaria sesgado
        y = (rg.random(200000) < p).astype(int); j = np.where(y == 1, rg.random(200000) < 0.95, rg.random(200000) < 0.30); self.assertGreater(j.mean() - p, 0.05)

    def test_ppi_reduce_varianza_frente_a_solo_oro_con_buen_juez(self):
        rg = np.random.default_rng(1); p = 0.5; a = []; b = []
        for _ in range(1500):
            y = (rg.random(2000) < p).astype(int); j = np.where(rg.random(2000) < 0.9, y, 1 - y); lab = np.arange(100)
            a.append(S.ppi_mean(j[100:], j[lab], y[lab])[0]); b.append(y[lab].mean())
        self.assertLess(np.var(a), np.var(b))


class TestPruebasMultiples(unittest.TestCase):
    def test_holm_y_bh_a_mano(self):
        p = np.array([0.01, 0.04, 0.03, 0.005]); self.assertTrue(np.allclose(S.holm(p), [0.03, 0.06, 0.06, 0.02]))
        self.assertTrue(np.allclose(S.benjamini_hochberg(p), [0.02, 0.04, 0.04, 0.02]))

    def test_propiedades(self):
        p = np.random.default_rng(0).random(50)
        for f in (S.holm, S.benjamini_hochberg): a = f(p); self.assertTrue((a >= p - 1e-12).all() and (a <= 1).all())
        self.assertTrue((S.holm(p) >= S.benjamini_hochberg(p) - 1e-12).all())

    def test_control_del_error_global(self):
        rg = np.random.default_rng(2); fw = 0
        for _ in range(2000): fw += (S.holm(rg.random(20)) < 0.05).any()
        self.assertLess(fw / 2000, 0.07)


if __name__ == "__main__":
    unittest.main()
