import importlib.util
from pathlib import Path
import sys
import unittest
import numpy as np

FILE = Path(__file__).resolve().parents[1] / "python" / "laboratorio.py"
spec = importlib.util.spec_from_file_location("mercado_liquidez", FILE)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class TestMarketLiquidity(unittest.TestCase):
    def test_es_discrete_fractional_tail(self):
        result = mod.tail_risk([0, 0, 10, 20], alpha=0.625)
        self.assertAlmostEqual(result.es, (20 + 0.5 * 10) / 1.5)
        self.assertGreaterEqual(result.es, result.var)

    def test_liquidity_first_breach(self):
        result = mod.liquidity_paths(5, [[0, 0, 0], [0, 0, 0]],
                                     [[2, 4, 1], [1, 1, 1]])
        self.assertEqual(result.first_breach.tolist(), [2, 4])
        self.assertEqual(result.breach_probability, 0.5)

    def test_margin_call_monotonicity(self):
        ins = np.zeros((2, 3))
        outs = np.ones((2, 3))
        base = mod.liquidity_paths(2, ins, outs)
        stress = mod.liquidity_paths(2, ins, outs, np.ones((2, 3)))
        self.assertGreaterEqual(stress.breach_probability, base.breach_probability)
        np.testing.assert_array_less(stress.paths, base.paths)

    def test_reproducible_stress(self):
        a, la = mod.correlated_stress(n_scenarios=100, horizon=4, seed=7)
        b, lb = mod.correlated_stress(n_scenarios=100, horizon=4, seed=7)
        np.testing.assert_array_equal(a, b)
        np.testing.assert_array_equal(la.paths, lb.paths)

    def test_interaction(self):
        self.assertAlmostEqual(mod.interaction_effect(1, 3, 4, 8), 2)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            mod.tail_risk([1, 2], alpha=1)
        with self.assertRaises(ValueError):
            mod.liquidity_paths(1, [[1]], [[-1]])


if __name__ == "__main__":
    unittest.main()
