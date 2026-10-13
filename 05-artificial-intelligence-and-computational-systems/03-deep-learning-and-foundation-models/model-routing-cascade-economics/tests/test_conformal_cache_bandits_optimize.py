import unittest
import numpy as np
import _path  # noqa: F401
from routerlab.world import World
from routerlab import conformal as CF
from routerlab.cache import simulate_cache
from routerlab.bandits import run_bandit
from routerlab.optimize import allocate, value, lp_upper_bound


class TestConformal(unittest.TestCase):
    def test_perdida_no_creciente_en_lambda(self):
        df = World().sample(5000, np.random.default_rng(0)); r = [CF.losses(df, l).mean() for l in np.linspace(0, 1.01, 30)]; self.assertTrue(np.all(np.diff(r) <= 1e-12)); self.assertEqual(CF.losses(df, 2.0).sum(), 0)

    def test_calibrar_cumple_la_condicion_en_calibracion(self):
        cal = World().sample(2000, np.random.default_rng(1)); eps = 0.05; lam = CF.calibrate_threshold(cal, eps); n = len(cal)
        self.assertLessEqual((n / (n + 1)) * CF.losses(cal, lam).mean() + 1 / (n + 1), eps + 1e-12)

    def test_umbral_minimal(self):
        cal = World().sample(2000, np.random.default_rng(1)); eps = 0.05; lam = CF.calibrate_threshold(cal, eps); n = len(cal); cands = np.sort(np.unique(cal.conf_small.values))
        menores = cands[cands < lam]
        if len(menores): self.assertGreater((n / (n + 1)) * CF.losses(cal, menores[-1]).mean() + 1 / (n + 1), eps)

    def test_epsilon_imposible_devuelve_infinito(self):
        cal = World().sample(50, np.random.default_rng(2)); self.assertEqual(CF.calibrate_threshold(cal, 0.001), float("inf"))

    def test_garantia_en_esperanza(self):
        w = World()
        for eps in (0.02, 0.05):
            r = CF.validate_guarantee(w, 300, 3000, eps, reps=250, seed=3); self.assertLessEqual(r["risk_mean"], eps + 0.004)

    def test_garantia_con_confianza_sobreconfiada(self):
        r = CF.validate_guarantee(World(conf_kind="overconfident"), 300, 3000, 0.03, reps=200, seed=4); self.assertLessEqual(r["risk_mean"], 0.03 + 0.004)

    def test_ahorro_crece_con_epsilon(self):
        w = World(); a = CF.validate_guarantee(w, 500, 3000, 0.02, 100, 5)["accept_mean"]; b = CF.validate_guarantee(w, 500, 3000, 0.08, 100, 5)["accept_mean"]; self.assertGreater(b, a)

    def test_ingenuo_viola_mas_con_pocos_datos(self):
        w = World(); c = CF.validate_guarantee(w, 60, 3000, 0.03, 300, 6, conservative=True); n = CF.validate_guarantee(w, 60, 3000, 0.03, 300, 6, conservative=False)
        self.assertGreater(n["risk_mean"], c["risk_mean"])


class TestCache(unittest.TestCase):
    def test_tau_mayor_a_1_no_hay_aciertos(self):
        r = simulate_cache(500, 20, 0.5, 1.0001, np.random.default_rng(0)); self.assertEqual(r["hit_rate"], 0.0)

    def test_aciertos_decrecen_con_tau(self):
        h = [simulate_cache(1500, 30, 0.6, t, np.random.default_rng(1))["hit_rate"] for t in (0.5, 0.7, 0.9, 0.99)]; self.assertTrue(np.all(np.diff(h) <= 1e-12))

    def test_errores_en_aciertos_decrecen_con_tau(self):
        e = [simulate_cache(2500, 30, 0.8, t, np.random.default_rng(2))["error_rate_on_hits"] for t in (0.3, 0.6, 0.9)]; self.assertGreater(e[0], e[-1])

    def test_sin_ruido_no_hay_errores(self):
        r = simulate_cache(1500, 30, 0.0, 0.99, np.random.default_rng(3)); self.assertEqual(r["error_rate_on_hits"], 0.0); self.assertGreater(r["hit_rate"], 0.8)

    def test_capacidad_acotada(self):
        a = simulate_cache(1500, 60, 0.3, 0.9, np.random.default_rng(4)); b = simulate_cache(1500, 60, 0.3, 0.9, np.random.default_rng(4), capacity=5); self.assertLess(b["hit_rate"], a["hit_rate"])


class TestBandits(unittest.TestCase):
    def test_arrepentimiento_sublineal_ucb_y_thompson(self):
        w = World()
        for algo in ("ucb", "thompson"):
            r = np.mean([run_bandit(w, 4000, 0.5, algo, np.random.default_rng(s))["regret"] for s in range(8)], axis=0); self.assertLess(r[3999] / r[1999], 1.7)

    def test_codicioso_sin_exploracion_puede_atascarse(self):
        w = World(); g = np.mean([run_bandit(w, 3000, 0.5, "greedy", np.random.default_rng(s))["regret"][-1] for s in range(20)]); t = np.mean([run_bandit(w, 3000, 0.5, "thompson", np.random.default_rng(s))["regret"][-1] for s in range(20)]); self.assertGreater(g, t)

    def test_mejor_brazo_cambia_con_lambda(self):
        w = World(); self.assertEqual(run_bandit(w, 200, 0.0, "ucb", np.random.default_rng(0))["best_arm"], "large"); self.assertEqual(run_bandit(w, 200, 5.0, "ucb", np.random.default_rng(0))["best_arm"], "small")

    def test_epsilon_codicioso_acumula_mas_que_ucb_con_epsilon_grande(self):
        w = World(); e = run_bandit(w, 3000, 0.5, "eps_greedy", np.random.default_rng(1), eps=0.5)["regret"][-1]; u = run_bandit(w, 3000, 0.5, "ucb", np.random.default_rng(1))["regret"][-1]; self.assertGreater(e, u)


class TestOptimize(unittest.TestCase):
    def datos(self, n, seed):
        rg = np.random.default_rng(seed); P = np.sort(rg.random((n, 3)), axis=1); return P, np.array([1.0, 6.0, 30.0])

    def test_factible_y_cota_lp(self):
        for seed in range(15):
            P, c = self.datos(60, seed); B = 0.3 * 30 * 60; a = allocate(P, c, B)
            self.assertLessEqual(c[a].sum(), B + 1e-9); ub = lp_upper_bound(P, c, B); self.assertLessEqual(value(P, a), ub + 1e-6); self.assertGreaterEqual(value(P, a), ub - 1.0)

    def test_presupuesto_amplio_asigna_el_mejor_nivel(self):
        P, c = self.datos(30, 0); self.assertTrue(np.all(allocate(P, c, 1e9) == 2))

    def test_presupuesto_minimo_asigna_el_mas_barato(self):
        P, c = self.datos(30, 1); self.assertTrue(np.all(allocate(P, c, 30.0) == 0))

    def test_valor_no_decrece_con_el_presupuesto(self):
        P, c = self.datos(50, 2); v = [value(P, allocate(P, c, b)) for b in (50, 200, 500, 1000, 1500)]; self.assertTrue(np.all(np.diff(v) >= -1e-9))

    def test_mejor_que_asignar_al_azar_con_el_mismo_gasto(self):
        P, c = self.datos(100, 3); B = 800.0; a = allocate(P, c, B); rg = np.random.default_rng(0); azar = []
        for _ in range(50):
            x = rg.integers(0, 3, 100)
            while c[x].sum() > B: x[rg.integers(0, 100)] = 0
            azar.append(value(P, x))
        self.assertGreater(value(P, a), np.mean(azar))


if __name__ == "__main__":
    unittest.main()
