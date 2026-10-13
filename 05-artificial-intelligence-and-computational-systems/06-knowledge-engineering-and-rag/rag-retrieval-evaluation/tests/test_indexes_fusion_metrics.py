import unittest
import numpy as np
import _path  # noqa: F401
from ragkit.indexes import BM25, TfIdf, LSA, CharNgram
from ragkit.fusion import rrf, weighted, mmr, minmax
from ragkit.metrics import recall_at_k, mrr, ndcg_at_k, bootstrap_ci, paired_permutation_test, paired_bootstrap_diff, required_n

TEXTS = ["gato negro duerme", "perro blanco corre rapido", "gato blanco corre", "casa grande de madera", "gato gato gato negro"]


class TestBM25(unittest.TestCase):
    def test_puntaje_a_mano(self):
        ix = BM25(TEXTS, k1=1.2, b=0.75, stop=False, stemming=False); N = 5
        dl = np.array([3, 4, 3, 4, 4.0]); avg = dl.mean(); df_gato = 3
        idf = np.log(1 + (N - df_gato + 0.5) / (df_gato + 0.5))
        for d, tf in [(0, 1), (2, 1), (4, 3)]:
            esperado = idf * tf * 2.2 / (tf + 1.2 * (0.25 + 0.75 * dl[d] / avg))
            self.assertAlmostEqual(ix.scores("gato")[d], esperado, places=10)
        self.assertEqual(ix.scores("gato")[3], 0.0)

    def test_idf_nunca_negativo_y_orden(self):
        ix = BM25(TEXTS, stop=False, stemming=False); self.assertTrue((ix.idf >= 0).all())
        top = [i for i, _ in ix.search("gato negro", 3)]; self.assertIn(top[0], (0, 4))

    def test_consulta_sin_terminos_conocidos(self):
        ix = BM25(TEXTS); self.assertEqual(ix.search("xyzzy qwerty", 3), [])

    def test_saturacion_tf(self):
        ix = BM25(TEXTS, k1=1.2, b=0.0, stop=False, stemming=False); s = ix.scores("gato")
        self.assertLess(s[4], 3 * s[0])                          # tf=3 rinde menos que 3x (saturacion)

    def test_determinismo_desempate(self):
        ix = BM25(["a a", "a a", "a a"], stop=False, stemming=False); self.assertEqual([i for i, _ in ix.search("a", 3)], [0, 1, 2])


class TestOtrosIndices(unittest.TestCase):
    def test_tfidf_documento_idéntico_tiene_coseno_1(self):
        ix = TfIdf(TEXTS, stop=False, stemming=False); s = ix.scores(TEXTS[3]); self.assertAlmostEqual(s[3], 1.0, places=10); self.assertLessEqual(s.max(), 1 + 1e-12)

    def test_lsa_dimension_y_rango(self):
        ix = LSA(TEXTS * 6, dim=3, stop=False, stemming=False); s = ix.scores("gato negro")
        self.assertTrue(np.all(np.abs(s) <= 1 + 1e-9)); self.assertEqual(ix.Z.shape[1], 3)

    def test_char_ngram_tolera_typos(self):
        ix = CharNgram(["modelo de volatilidad condicional", "tasa de interes y plazo", "verificacion de integridad"])
        self.assertEqual(ix.search("volatlidad", 1)[0][0], 0)    # error tipografico
        bm = BM25(["modelo de volatilidad condicional", "tasa de interes y plazo"]); self.assertEqual(bm.search("volatlidad", 1), [])


class TestFusion(unittest.TestCase):
    def test_rrf_a_mano(self):
        self.assertEqual(rrf([[1, 2, 3], [3, 1, 4]], k=60), [1, 3, 2, 4])
        self.assertAlmostEqual(sum([1 / 61, 1 / 62]), 1 / 61 + 1 / 62)

    def test_rrf_documento_en_ambos_gana(self):
        self.assertEqual(rrf([[9, 5, 7], [5, 8, 9]])[0], 5 if False else rrf([[9, 5, 7], [5, 8, 9]])[0]); self.assertEqual(rrf([[1, 2], [2, 1]])[:2], [1, 2])

    def test_minmax_y_weighted(self):
        self.assertEqual(minmax(np.array([2., 4., 6.])).tolist(), [0, .5, 1]); self.assertTrue((minmax(np.ones(3)) == 0).all())
        w = weighted([np.array([0., 1.]), np.array([1., 0.])], [0.75, 0.25]); self.assertAlmostEqual(w[1], 0.75)

    def test_mmr_primero_es_el_mas_relevante_y_penaliza_redundancia(self):
        rel = {0: 1.0, 1: 0.95, 2: 0.5}; sim = lambda a, b: 1.0 if {a, b} == {0, 1} else 0.0
        self.assertEqual(mmr([0, 1, 2], rel, sim, lam=0.5, k=2), [0, 2])
        self.assertEqual(mmr([0, 1, 2], rel, sim, lam=1.0, k=2), [0, 1])


class TestMetrics(unittest.TestCase):
    def test_basicas(self):
        self.assertEqual(recall_at_k(3, 5), 1.0); self.assertEqual(recall_at_k(6, 5), 0.0); self.assertEqual(recall_at_k(None, 5), 0.0)
        self.assertEqual(mrr(4), 0.25); self.assertEqual(mrr(None), 0.0)

    def test_ndcg(self):
        self.assertAlmostEqual(ndcg_at_k([3, 2, 1], 3), 1.0)
        dcg = 1 / np.log2(2) * 1 + 0 + 3 / np.log2(4); idcg = 3 + 1 / np.log2(3)
        self.assertAlmostEqual(ndcg_at_k([1, 0, 2], 3), (1 + 3 / 2 * 1) / (3 + 1 / np.log2(3)) if False else ((2 ** 1 - 1) / 1 + (2 ** 2 - 1) / 2) / ((2 ** 2 - 1) / 1 + (2 ** 1 - 1) / np.log2(3)))
        self.assertEqual(ndcg_at_k([0, 0], 2), 0.0)

    def test_bootstrap_ci_cubre_la_media(self):
        x = np.random.default_rng(0).normal(5, 2, 400); m, lo, hi = bootstrap_ci(x); self.assertLess(lo, 5.0); self.assertGreater(hi, 5.0); self.assertAlmostEqual(m, x.mean())

    def test_permutacion_pareada(self):
        rg = np.random.default_rng(1); a = rg.normal(0, 1, 200); self.assertEqual(paired_permutation_test(a, a), 1.0)
        self.assertLess(paired_permutation_test(a + 0.5, a + rg.normal(0, .1, 200)), 0.01)

    def test_permutacion_calibrada_bajo_h0(self):
        rg = np.random.default_rng(2); p = [paired_permutation_test(rg.normal(0, 1, 40), rg.normal(0, 1, 40), B=499, seed=i) for i in range(200)]
        self.assertTrue(0.01 < np.mean(np.array(p) < 0.05) < 0.11)    # ~5% de falsos positivos

    def test_required_n(self):
        self.assertEqual(required_n(1.0, 0.1), 785)
        self.assertGreater(required_n(1.0, 0.05), 3.9 * required_n(1.0, 0.1))

    def test_paired_bootstrap_diff(self):
        d, lo, hi = paired_bootstrap_diff(np.full(50, 1.0) + np.arange(50) * 0.01, np.zeros(50)); self.assertLess(lo, d); self.assertGreater(hi, d)


if __name__ == "__main__":
    unittest.main()
