import unittest
import numpy as np
import _path  # noqa: F401
from agentrt.policies import RetryPolicy, RetryBudget, CircuitBreaker, BudgetGuard, BudgetExceeded, LoopDetector


class TestRetryPolicy(unittest.TestCase):
    def test_sin_jitter_es_exponencial_con_tope(self):
        p = RetryPolicy(5, base=0.1, cap=1.0, jitter="none"); rg = np.random.default_rng(0)
        self.assertEqual([p.delay(k, rg) for k in range(1, 6)], [0.1, 0.2, 0.4, 0.8, 1.0])

    def test_rangos_por_tipo_de_jitter(self):
        rg = np.random.default_rng(1)
        for k in (1, 3, 6):
            techo = min(10.0, 0.1 * 2 ** (k - 1))
            full = [RetryPolicy(jitter="full").delay(k, rg) for _ in range(400)]; self.assertTrue(0 <= min(full) and max(full) <= techo)
            eq = [RetryPolicy(jitter="equal").delay(k, rg) for _ in range(400)]; self.assertTrue(techo / 2 <= min(eq) and max(eq) <= techo)
            self.assertAlmostEqual(np.mean(full), techo / 2, delta=0.12 * techo + 0.01)

    def test_decorrelado_acotado(self):
        rg = np.random.default_rng(2); pol = RetryPolicy(jitter="decorrelated", base=0.1, cap=5.0); prev = None
        for k in range(1, 40): prev = pol.delay(k, rg, prev); self.assertTrue(0.1 <= prev <= 5.0)

    def test_jitter_invalido(self):
        with self.assertRaises(ValueError): RetryPolicy(jitter="x").delay(1, np.random.default_rng(0))


class TestRetryBudget(unittest.TestCase):
    def test_deposito_tope_y_consumo(self):
        b = RetryBudget(ratio=0.5, max_tokens=2.0, initial=0.0)
        self.assertFalse(b.try_retry()); b.on_request(); b.on_request(); self.assertTrue(b.try_retry()); self.assertFalse(b.try_retry())
        for _ in range(20): b.on_request()
        self.assertEqual(b.tokens, 2.0)

    def test_amplificacion_acotada_a_largo_plazo(self):
        b = RetryBudget(ratio=0.1, max_tokens=10.0, initial=0.0); reintentos = 0
        for _ in range(10_000):
            b.on_request()
            while b.try_retry(): reintentos += 1                  # servicio caido: todo reintento posible se consume
        self.assertAlmostEqual(reintentos / 10_000, 0.1, delta=0.002)


class TestCircuitBreaker(unittest.TestCase):
    def mk(self): return CircuitBreaker(threshold=0.5, window=10, min_calls=4, cooldown=5.0, probes=2)

    def test_no_abre_antes_de_min_calls(self):
        cb = self.mk()
        for _ in range(3): cb.allow(0); cb.record(False, 0)
        self.assertEqual(cb.state, "closed")

    def test_abre_rechaza_semiabre_y_cierra(self):
        cb = self.mk()
        for _ in range(4): self.assertTrue(cb.allow(0)); cb.record(False, 0)
        self.assertEqual(cb.state, "open"); self.assertFalse(cb.allow(1.0)); self.assertFalse(cb.allow(4.9))
        self.assertTrue(cb.allow(5.0)); self.assertEqual(cb.state, "half_open"); cb.record(True, 5.0)
        self.assertTrue(cb.allow(5.1)); cb.record(True, 5.1); self.assertEqual(cb.state, "closed")
        self.assertEqual([s for _, s in cb.transitions], ["open", "half_open", "closed"])

    def test_semiabierto_limita_sondas_y_vuelve_a_abrir_si_falla(self):
        cb = self.mk()
        for _ in range(4): cb.allow(0); cb.record(False, 0)
        self.assertTrue(cb.allow(5.0)); self.assertTrue(cb.allow(5.0)); self.assertFalse(cb.allow(5.0))      # solo 2 sondas
        cb.record(False, 5.0); self.assertEqual(cb.state, "open"); self.assertFalse(cb.allow(6.0))

    def test_no_abre_con_tasa_de_fallos_baja(self):
        cb = self.mk(); rg = np.random.default_rng(0)
        for i in range(200): cb.allow(i); cb.record(bool(rg.random() > 0.1), i)
        self.assertEqual(cb.state, "closed")


class TestGuardas(unittest.TestCase):
    def test_presupuesto(self):
        g = BudgetGuard(max_steps=3)
        for _ in range(3): g.charge()
        with self.assertRaises(BudgetExceeded): g.charge()
        with self.assertRaises(BudgetExceeded): BudgetGuard(max_cost=1.0).charge(cost=1.5)
        with self.assertRaises(BudgetExceeded): BudgetGuard(max_tokens=10).charge(tokens=11)

    def test_detector_de_bucles(self):
        d = LoopDetector(max_repeats=3, window=6)
        self.assertFalse(d.observe("t", 1)); self.assertFalse(d.observe("t", 1)); self.assertTrue(d.observe("t", 1))

    def test_detector_no_marca_llamadas_distintas_ni_antiguas(self):
        d = LoopDetector(max_repeats=3, window=4)
        for i in range(10): self.assertFalse(d.observe("t", i))
        d2 = LoopDetector(max_repeats=3, window=4); d2.observe("t", 1); d2.observe("t", 1)
        for i in range(4): d2.observe("u", i)
        self.assertFalse(d2.observe("t", 1))                       # las anteriores salieron de la ventana


if __name__ == "__main__":
    unittest.main()
