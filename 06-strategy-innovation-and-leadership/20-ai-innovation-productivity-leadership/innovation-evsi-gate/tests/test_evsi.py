import unittest
from dataclasses import replace
import math
from src.evsi import Case, choose, evaluate, predictive


class DecisionTests(unittest.TestCase):
    def test_uniform_predictive_oracle(self):
        c = Case(alpha=1, beta=1)
        for n in (0, 1, 10, 100):
            for p in predictive(c, n):
                self.assertAlmostEqual(p, 1 / (n + 1), places=12)

    def test_no_information(self):
        self.assertAlmostEqual(evaluate(Case(), 0)['evsi'], 0)

    def test_information_properties(self):
        for a in (0.5, 1, 6, 30):
            for b in (0.5, 4, 20):
                c = Case(alpha=a, beta=b)
                values = [float(evaluate(c, n)['evsi']) for n in range(21)]
                self.assertGreaterEqual(min(values), -1e-8)
                self.assertTrue(all(y >= x - 1e-8 for x, y in zip(values, values[1:])))
                self.assertGreaterEqual(float(choose(c, [0, 10, 20])['net_value']),
                                        float(evaluate(c, 0)['net_value']) - 1e-8)

    def test_gate_and_expensive_ablation(self):
        self.assertEqual(choose(Case(), [0, 10, 50, 100])['action'], 'experimentar')
        self.assertEqual(choose(replace(Case(), experiment_fixed=1e6), [0, 100])['n'], 0)
        self.assertEqual(choose(replace(Case(), alpha=1000, beta=1), [0, 10])['action'], 'escalar')
        self.assertEqual(choose(replace(Case(), alpha=1, beta=1000), [0, 10])['action'], 'detener')

    def test_evpi_upper_bound_independent_quadrature(self):
        from scipy.integrate import quad
        from scipy.stats import beta
        for a, b in ((1, 1), (6, 4), (30, 20)):
            c = Case(alpha=a, beta=b)
            perfect = quad(lambda p: max(0, c.payoff(p)) * beta.pdf(p, a, b),
                           0, 1, points=[0.6], epsabs=1e-6)[0]
            bound = perfect - float(evaluate(c, 0)['net_value'])
            for n in (0, 10, 100, 1000):
                self.assertLessEqual(float(evaluate(c, n)['evsi']), bound + 1e-6)

    def test_invalid(self):
        for args in ({'alpha': 0}, {'beta': -1}, {'unit_cost': -1},
                     {'population': -1}, {'benefit': math.nan}):
            with self.assertRaises(ValueError):
                Case(**args)
        for n in (-1, 1.2, True):
            with self.assertRaises(ValueError):
                evaluate(Case(), n)
        with self.assertRaises(ValueError):
            choose(Case(), [10])
