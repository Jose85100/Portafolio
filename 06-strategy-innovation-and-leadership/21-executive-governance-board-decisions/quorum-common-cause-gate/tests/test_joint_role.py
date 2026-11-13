import unittest
from itertools import product
import numpy as np
from scipy.optimize import linprog
from src.joint_role import joint_bounds, select_joint
from src.reserve_ambiguity import ReservePlan, choose_plan


class JointRoleTests(unittest.TestCase):
    def test_lp_oracle_grid_and_witness(self):
        states = np.array(list(product((0, 1), repeat=3)))
        matrix = np.vstack((np.ones(8), states.T))
        for r, q1, q2 in product((0, .2, .7, .95, 1), repeat=3):
            b = joint_bounds(ReservePlan('p', q1, q2, 1), shock=1, risk=r)
            for sign, key in ((1, 'lower'), (-1, 'upper')):
                objective = np.zeros(8)
                objective[-1] = sign
                lp = linprog(objective, A_eq=matrix, b_eq=[1, r, q1, q2],
                             bounds=(0, None), method='highs')
                self.assertTrue(lp.success)
                self.assertAlmostEqual(sign*lp.fun, b[key], places=10)
                self.assertLess(np.max(np.abs(matrix@lp.x - [1, r, q1, q2])), 1e-10)
                self.assertGreaterEqual(min(lp.x), -1e-10)

    def test_restriction_and_monotonicity(self):
        for r, q in product((0, .5, .95, 1), (0, .4, .8, 1)):
            b = joint_bounds(ReservePlan('p', q, q, 1), risk=r)
            self.assertLessEqual(b['lower'], b['restricted_lower30']+1e-12)
            self.assertLessEqual(b['restricted_lower30'], b['nominal']+1e-12)
            self.assertLessEqual(b['nominal'], b['upper']+1e-12)
            self.assertLessEqual(b['upper'], r+1e-12)
            larger = joint_bounds(ReservePlan('p', min(1, q+.01), q, 1), risk=r)
            self.assertGreaterEqual(larger['lower']+1e-12, b['lower'])

    def test_exact_recovery_role_certain_and_no_shock(self):
        p = ReservePlan('p', .7, .9, 1)
        b = joint_bounds(p, risk=1)
        self.assertAlmostEqual(b['lower'], b['restricted_lower30'])
        b = joint_bounds(p, shock=0)
        self.assertEqual(b['lower'], .95)
        self.assertEqual(b['upper'], .95)

    def test_decision_boundary_and_negative(self):
        plans = [ReservePlan('A', .7, .7, 2), ReservePlan('B', .8, .8, 3),
                 ReservePlan('C', .9, .9, 4)]
        self.assertEqual(choose_plan(plans, target=.872)['name'], 'B')
        self.assertEqual(select_joint(plans, target=.872).name, 'C')
        self.assertEqual(select_joint(plans).name, 'B')
        with self.assertRaises(ValueError):
            select_joint(plans, target=.97)
        self.assertAlmostEqual(joint_bounds(plans[1])['lower'], .87)

    def test_invalid_and_ties(self):
        p = ReservePlan('p', .8, .8, 1)
        for r, s in ((float('nan'), .2), (-.1, .2), (.95, 2)):
            with self.assertRaises(ValueError):
                joint_bounds(p, s, r)
        for menu, target in (([], .8), ([p, p], .8), ([p], float('nan'))):
            with self.assertRaises(ValueError):
                select_joint(menu, target)
        self.assertEqual(select_joint([ReservePlan('b', 1, 1, 1),
                                      ReservePlan('a', 1, 1, 1)]).name, 'a')
