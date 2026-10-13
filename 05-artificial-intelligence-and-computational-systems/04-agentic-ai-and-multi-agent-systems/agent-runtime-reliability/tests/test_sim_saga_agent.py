import unittest
import numpy as np
import _path  # noqa: F401
from agentrt.policies import RetryPolicy, RetryBudget, CircuitBreaker, BudgetGuard, LoopDetector
from agentrt.sim import simulate_service, SimTool, Ledger, call_with_retries
from agentrt.saga import Step, run_saga, net_state
from agentrt.agent import run_agent


class TestService(unittest.TestCase):
    def test_goodput_y_amplificacion_analiticos_sin_saturacion(self):
        p, n = 0.3, 4; pol = RetryPolicy(n, base=0.5, cap=2.0, jitter="full")
        r = simulate_service(np.full(300, 200), 10 ** 9, p, pol, np.random.default_rng(0))
        self.assertAlmostEqual(r["goodput"], 1 - p ** n, delta=0.01)
        self.assertAlmostEqual(r["amplification"], (1 - p ** n) / (1 - p), delta=0.02)

    def test_sin_reintentos(self):
        r = simulate_service(np.full(200, 100), 10 ** 9, 0.2, RetryPolicy(1), np.random.default_rng(1))
        self.assertAlmostEqual(r["goodput"], 0.8, delta=0.01); self.assertAlmostEqual(r["amplification"], 1.0, places=9)

    def test_conservacion_ok_mas_fallos_igual_total(self):
        r = simulate_service(np.full(100, 50), 60, 0.1, RetryPolicy(3), np.random.default_rng(2))
        self.assertEqual(round(r["goodput"] * r["total"]) + r["failed"], r["total"])

    def test_determinismo(self):
        a = simulate_service(np.full(50, 30), 40, 0.1, RetryPolicy(3), np.random.default_rng(3)); b = simulate_service(np.full(50, 30), 40, 0.1, RetryPolicy(3), np.random.default_rng(3))
        self.assertEqual(a["goodput"], b["goodput"]); self.assertTrue(np.array_equal(a["offered"], b["offered"]))

    def test_presupuesto_de_reintentos_acota_la_carga(self):
        arr = np.full(200, 100); cap = np.r_[np.full(50, 200), np.full(30, 20), np.full(120, 200)]
        sin = simulate_service(arr, cap, 0.0, RetryPolicy(5, 0.2, 5.0, "full"), np.random.default_rng(4))
        con = simulate_service(arr, cap, 0.0, RetryPolicy(5, 0.2, 5.0, "full"), np.random.default_rng(4), budget=RetryBudget(0.1, 10.0))
        self.assertLess(con["offered"].max(), sin["offered"].max()); self.assertLess(con["amplification"], sin["amplification"])

    def test_cortacircuitos_rechaza_con_servicio_caido(self):
        arr = np.full(100, 50); cap = np.r_[np.full(20, 200), np.zeros(40) + 0.001, np.full(140, 200)]
        r = simulate_service(arr, cap, 0.0, RetryPolicy(3, 0.2, 2.0), np.random.default_rng(5), breaker=CircuitBreaker(0.5, 20, 10, 5.0, 3))
        self.assertGreater(r["rejected_by_breaker"], 0)


class TestIdempotencia(unittest.TestCase):
    def run_ops(self, idempotent, use_key, p_lost=0.3, n=3000):
        led = Ledger(); tool = SimTool(led, p_fail_before=0.0, p_lost=p_lost, idempotent=idempotent); rg = np.random.default_rng(7); pol = RetryPolicy(8, 0.01, 0.1)
        res = [call_with_retries(tool, i, pol, rg, use_key) for i in range(n)]; return led, tool, res

    def test_sin_clave_hay_efectos_duplicados(self):
        led, tool, res = self.run_ops(False, False); self.assertGreater(led.duplicates(), 0)

    def test_duplicados_esperados_son_geometricos(self):
        led, _, _ = self.run_ops(False, False, p_lost=0.3, n=6000)
        # sin idempotencia cada intento aplica el efecto; los intentos continuan mientras se pierde la respuesta
        # aplicaciones por operacion ~ sum_{k<8} 0.3^k => duplicados por op = aplicaciones - 1
        esperado = sum(0.3 ** k for k in range(8)) - 1; self.assertAlmostEqual(led.duplicates() / 6000, esperado, delta=0.02)

    def test_con_clave_el_efecto_es_exactamente_una_vez(self):
        led, tool, res = self.run_ops(True, True); self.assertEqual(led.duplicates(), 0); self.assertEqual(led.total(), 3000)

    def test_con_clave_distinta_por_intento_no_deduplica(self):
        led, _, _ = self.run_ops(True, False); self.assertGreater(led.duplicates(), 0)


class TestSaga(unittest.TestCase):
    def test_invariante_todo_o_nada_con_compensaciones_fiables(self):
        rg = np.random.default_rng(0); steps = [Step("a", 0.2), Step("b", 0.2), Step("c", 0.2)]; estados = {"committed": 0, "compensated": 0}
        for _ in range(1500):
            led = Ledger(); r = run_saga(steps, led, rg); ns = net_state(led, 3); estados[r["status"]] += 1
            self.assertTrue(all(x in (0, 1) for x in ns))
            self.assertEqual(ns, [1, 1, 1] if r["status"] == "committed" else [0, 0, 0])
        self.assertAlmostEqual(estados["committed"] / 1500, 0.8 ** 3, delta=0.03)

    def test_compensacion_que_siempre_falla_deja_estado_atascado(self):
        led = Ledger(); r = run_saga([Step("a", 0.0, 1.0), Step("b", 1.0)], led, np.random.default_rng(1)); self.assertEqual(r["status"], "stuck"); self.assertEqual(net_state(led, 2), [1, 0])

    def test_prob_atasco_analitica(self):
        rg = np.random.default_rng(2); steps = [Step("a", 0.0, 0.5), Step("b", 1.0)]; stuck = 0; R = 4000
        for _ in range(R): stuck += run_saga(steps, Ledger(), rg, comp_retries=3)["status"] == "stuck"
        self.assertAlmostEqual(stuck / R, 0.5 ** 3, delta=0.02)


class TestAgente(unittest.TestCase):
    def test_bucle_infinito_lo_detiene_el_presupuesto(self):
        r = run_agent(lambda h: ("buscar", len(h)), lambda t, a: ("x", 1.0), BudgetGuard(max_steps=20), None); self.assertTrue(r["stop"].startswith("budget")); self.assertEqual(r["steps"], 21)

    def test_bucle_identico_lo_detecta_el_detector(self):
        r = run_agent(lambda h: ("buscar", "igual"), lambda t, a: ("x", 1.0), BudgetGuard(max_steps=100), LoopDetector(3, 10)); self.assertEqual(r["stop"], "loop_detected"); self.assertEqual(r["steps"], 2)

    def test_agente_normal_termina(self):
        r = run_agent(lambda h: ("t", len(h)) if len(h) < 5 else None, lambda t, a: ("x", 0.5), BudgetGuard(max_steps=50), LoopDetector(3, 10)); self.assertEqual(r, {"stop": "done", "steps": 5, "cost": 2.5})

    def test_sin_guardas_corta_el_limite_duro(self):
        r = run_agent(lambda h: ("t", len(h)), lambda t, a: ("x", 1.0), None, None, max_hard=100); self.assertEqual(r["stop"], "hard_limit")


if __name__ == "__main__":
    unittest.main()
