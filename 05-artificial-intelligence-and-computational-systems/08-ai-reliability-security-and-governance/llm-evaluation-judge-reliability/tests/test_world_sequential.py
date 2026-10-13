import unittest
import numpy as np
import _path  # noqa: F401
from evalkit import world as W, sequential as Q


class TestMundo(unittest.TestCase):
    def test_probabilidad_de_acierto_monotona(self):
        d = np.linspace(-2, 2, 9); p = W.p_correct(0.3, d); self.assertTrue((np.diff(p) < 0).all()); self.assertAlmostEqual(W.p_correct(0.0, np.array([0.0]))[0], 0.5)
        self.assertTrue((W.p_correct(1.0, d) > W.p_correct(0.0, d)).all())

    def test_muestras_repetidas_correlacionadas_dentro_del_item(self):
        rg = np.random.default_rng(0); items = W.make_items(2000, rg); y = W.sample_correct(0.0, items, rg, k=2)
        self.assertGreater(np.corrcoef(y[:, 0], y[:, 1])[0, 1], 0.1)

    def test_juez_tpr_tnr(self):
        rg = np.random.default_rng(1); t = rg.integers(0, 2, 200000); v = rg.standard_normal(200000); j = W.judge_labels(t, v, rg, 0.9, 0.8)
        self.assertAlmostEqual(j[t == 1].mean(), 0.9, delta=0.005); self.assertAlmostEqual(1 - j[t == 0].mean(), 0.8, delta=0.005)

    def test_sesgo_de_verbosidad_cambia_la_tasa_de_pase(self):
        rg = np.random.default_rng(2); t = np.zeros(100000, int); v = rg.standard_normal(100000)
        self.assertAlmostEqual(W.judge_labels(t, v, rg, 0.9, 0.85, 0.0).mean(), 0.15, delta=0.01)
        j = W.judge_labels(t, v, rg, 0.9, 0.85, 1.0); self.assertGreater(j[v > 1].mean(), j[v < -1].mean() + 0.3)

    def test_sesgo_de_posicion_y_simetria_con_intercambio(self):
        rg = np.random.default_rng(3); qa = qb = np.zeros(200000)
        a = W.pairwise_judge(qa, qb, rg, position_bias=1.0).mean(); self.assertAlmostEqual(a, W.sigmoid(1.0), delta=0.005)
        b = W.pairwise_judge(qa, qb, rg, position_bias=1.0, swapped=True).mean(); self.assertAlmostEqual(a + b, 1.0, delta=0.01)    # el sesgo favorece al primero visto


class TestSecuencial(unittest.TestCase):
    def test_fronteras_de_wald(self):
        A, B = Q.sprt_bounds(0.05, 0.2); self.assertAlmostEqual(A, np.log(0.8 / 0.05)); self.assertAlmostEqual(B, np.log(0.2 / 0.95)); self.assertGreater(A, 0); self.assertLess(B, 0)

    def test_tasas_de_error_del_sprt(self):
        rg = np.random.default_rng(0); R = 1500; fp = 0; det = 0
        for _ in range(R):
            o0 = np.where(rg.random(400) < 0.5, 1, -1); fp += Q.sprt_regression(o0, 0.5, 0.7, 0.05, 0.2)[0] == "H1"
            o1 = np.where(rg.random(400) < 0.7, 1, -1); det += Q.sprt_regression(o1, 0.5, 0.7, 0.05, 0.2)[0] == "H1"
        self.assertLess(fp / R, 0.05 + 0.015); self.assertGreater(det / R, 0.8 - 0.05)

    def test_sprt_ignora_concordantes(self):
        self.assertEqual(Q.sprt_regression(np.zeros(100), 0.5, 0.7)[0], "continuar")

    def test_gate_fixed(self):
        self.assertEqual(Q.gate_fixed(np.r_[np.ones(30), -np.ones(5)]), "H1"); self.assertEqual(Q.gate_fixed(np.r_[np.ones(10), -np.ones(10)]), "H0"); self.assertEqual(Q.gate_fixed(np.zeros(5)), "H0")


if __name__ == "__main__":
    unittest.main()
