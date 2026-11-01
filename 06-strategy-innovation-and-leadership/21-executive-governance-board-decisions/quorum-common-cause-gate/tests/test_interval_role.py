import unittest
from itertools import product
import numpy as np
from src.interval_role import ProbabilityInterval as PI, IntervalPlan, interval_bounds, select_interval
from src.joint_role import joint_bounds
from src.reserve_ambiguity import ReservePlan
from benchmarks.interval_run import lp_bounds, load_config, point_baseline


class IntervalRoleTests(unittest.TestCase):
    def test_inequality_lp_oracle_and_witnesses(self):
        for r, q1, q2, s in product((PI(0, 0), PI(.2, .8), PI(1, 1)), repeat=4):
            p = IntervalPlan('p', q1, q2, 0)
            b = interval_bounds(p, r, s)
            for upper, key in ((False, 'lower'), (True, 'upper')):
                value, mass, states = lp_bounds(p, r, s, upper)
                self.assertAlmostEqual(value, b[key], places=10)
                self.assertAlmostEqual(sum(mass), 1)
                self.assertGreaterEqual(min(mass), -1e-10)
                for marginal, interval in zip(states.T@mass, (r, q1, q2)):
                    self.assertGreaterEqual(marginal+1e-10, interval.lower)
                    self.assertLessEqual(marginal, interval.upper+1e-10)

    def test_point_recovery_and_order(self):
        for r, q1, q2, s in product((0, .5, 1), repeat=4):
            p = IntervalPlan('p', PI(q1, q1), PI(q2, q2), 0)
            b = interval_bounds(p, PI(r, r), PI(s, s))
            exact = joint_bounds(ReservePlan('p', q1, q2, 0), s, r)
            self.assertAlmostEqual(b['lower'], exact['lower'], places=12)
            self.assertAlmostEqual(b['upper'], exact['upper'], places=12)
            self.assertLessEqual(b['lower'], b['upper']+1e-12)

    def test_nested_boxes_cannot_improve_certificate(self):
        previous = 1.0
        previous_upper = 0.0
        for a in np.linspace(0, 1, 101):
            q = PI(.8-.02*a, .8+.02*a)
            b = interval_bounds(IntervalPlan('p', q, q, 1), PI(.95-.01*a, .95+.01*a), PI(.2-.01*a, .2+.01*a))
            self.assertLessEqual(b['lower'], previous+1e-12)
            self.assertGreaterEqual(b['upper']+1e-12, previous_upper)
            previous, previous_upper = b['lower'], b['upper']

    def test_same_target_changes_decision_and_infeasibility(self):
        cfg, plans, risk, shock = load_config()
        self.assertEqual(select_interval(plans, risk, shock, cfg['target']).name, 'C')
        self.assertAlmostEqual(interval_bounds(plans[1], risk, shock)['lower'], .8476)
        with self.assertRaises(ValueError):
            select_interval(plans, risk, shock, .97)
        certain = PI(1, 1)
        self.assertEqual(interval_bounds(IntervalPlan('p', certain, certain, 0), certain, PI(0, 1)), {'lower': 1., 'upper': 1.})

    def test_baseline_uses_config_centers_and_reports_infeasibility(self):
        q = PI(.9, 1)
        plans = [IntervalPlan('custom', q, q, 1)]
        points, r, s, selected = point_baseline(plans, PI(.4, .6), PI(.7, .9), .85)
        self.assertAlmostEqual(r, .5)
        self.assertAlmostEqual(s, .8)
        self.assertEqual(selected, 'infeasible')
        self.assertLess(joint_bounds(points[0], s, r)['lower'], .85)
        self.assertEqual(point_baseline(plans, PI(1, 1), PI(0, 0), .85)[-1], 'custom')

    def test_validation_and_ties(self):
        for a, b in ((.8, .2), (-.1, .2), (.2, 1.1), (float('nan'), 1), (0, float('inf'))):
            with self.assertRaises(ValueError):
                PI(a, b)
        q = PI(1, 1)
        for name, cost in (('', 1), ('p', -1), ('p', float('nan'))):
            with self.assertRaises(ValueError):
                IntervalPlan(name, q, q, cost)
        p = IntervalPlan('a', q, q, 1)
        for menu, target in (([], .85), ([p, p], .85), ([p], float('nan'))):
            with self.assertRaises(ValueError):
                select_interval(menu, q, q, target)
        self.assertEqual(select_interval([IntervalPlan('b', q, q, 1), p], q, q).name, 'a')
