import unittest
from src.pricing import Scenario, choose, cvar, profit


class PricingTests(unittest.TestCase):
    def test_fractional_atom(self):
        self.assertAlmostEqual(cvar([0, 10], [.7, .3], .8), 10)
        self.assertAlmostEqual(cvar([0, 10], [.7, .3], .5), 6)
        self.assertAlmostEqual(cvar([0, 10], [.7, .3], 0), 3)

    def test_cvar_lp_oracle(self):
        import numpy as np
        from scipy.optimize import linprog
        losses = np.array([0, 4, 11, 30], dtype=float)
        weights = np.array([.37, .23, .29, .11])
        for alpha in (0, .5, .8, .95):
            # min eta + sum w*z/(1-alpha), z>=loss-eta, z>=0.
            objective = np.r_[1, weights/(1-alpha)]
            matrix = np.column_stack([-np.ones(4), -np.eye(4)])
            answer = linprog(objective, A_ub=matrix, b_ub=-losses,
                             bounds=[(None, None)]+[(0, None)]*4, method='highs')
            self.assertTrue(answer.success)
            self.assertAlmostEqual(cvar(list(losses), list(weights), alpha), answer.fun, places=9)

    def test_cvar_translation_homogeneity_monotonicity(self):
        x, w = [1, 3, 12], [.2, .5, .3]
        for alpha in (0, .5, .9):
            self.assertAlmostEqual(cvar([v+7 for v in x], w, alpha), cvar(x, w, alpha)+7)
            self.assertAlmostEqual(cvar([2*v for v in x], w, alpha), 2*cvar(x, w, alpha))
        self.assertLessEqual(cvar(x, w, .5), cvar(x, w, .9))

    def test_capacity_and_extremes(self):
        s = Scenario('stress', 1, 1000)
        self.assertEqual(profit(20, s, 0, 4, 1000), -1000)
        self.assertLessEqual(profit(20, s, 300, 4, 1000), (20-4)*300-1000)
        self.assertEqual(profit(1e6, s, 300, 4, 1000), -1000)

    def test_stop_and_nested_budget(self):
        scenarios = [Scenario('one', 1, 60)]
        for budget in (0, 100, 500):
            decision = choose([10, 20, 30], scenarios, 300, 4, 1000, .9, budget)
            self.assertIsNone(decision['price'])
        scenarios = [Scenario('up', .6, 1000), Scenario('mid', .25, 250), Scenario('down', .15, 60)]
        values = [choose(list(range(8, 41, 2)), scenarios, 300, 4, 1000, .9, b)['expected_profit'] for b in (0, 500, 1000)]
        self.assertEqual(values, sorted(values))

    def test_invalid(self):
        for params in (dict(weight=0, arrivals=1), dict(weight=1, arrivals=-1), dict(weight=1, arrivals=1, elasticity=0), dict(weight=1, arrivals=float('nan'))):
            with self.assertRaises(ValueError):
                Scenario('bad', **params)
        for losses, weights, alpha in (([], [], .9), ([1], [0], .9), ([1], [.5], .9), ([1], [1], 1), ([float('nan')], [1], .9)):
            with self.assertRaises(ValueError):
                cvar(losses, weights, alpha)
        with self.assertRaises(ValueError):
            choose([1], [Scenario('one', 1, 1)], 1, 1, 1, .9, -1)
        with self.assertRaises(ValueError):
            profit(-1, Scenario('one', 1, 1), 1, 1, 1)
