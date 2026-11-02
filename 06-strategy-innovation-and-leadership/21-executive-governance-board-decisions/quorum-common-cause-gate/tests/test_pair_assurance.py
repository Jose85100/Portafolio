import unittest
from itertools import product
import numpy as np
from src.interval_role import ProbabilityInterval as PI, IntervalPlan, interval_bounds
from src.pair_assurance import pair_lower, required_pair_floor, choose_pair
from benchmarks.pair_run import lp_pair, load_pair_config


class PairAssuranceTests(unittest.TestCase):
    def test_lp_oracle_and_feasible_witnesses(self):
        for risk, q1, q2, shock in product((PI(0, 0), PI(.2, .8), PI(1, 1)), repeat=4):
            p = IntervalPlan('p', q1, q2, 0)
            cap = min(q1.upper, q2.upper)
            for floor in sorted({0., cap/2, cap}):
                value, mass, states = lp_pair(p, risk, shock, floor)
                self.assertAlmostEqual(value, pair_lower(p, risk, shock, floor), places=10)
                self.assertAlmostEqual(sum(mass), 1)
                self.assertGreaterEqual(min(mass), -1e-10)
                for marginal, interval in zip(states.T@mass, (risk, q1, q2)):
                    self.assertGreaterEqual(marginal+1e-10, interval.lower)
                    self.assertLessEqual(marginal, interval.upper+1e-10)
                self.assertGreaterEqual((states[:, 1]*states[:, 2])@mass+1e-10, floor)

    def test_recovery_and_nested_constraint_monotonicity(self):
        cfg, plans, risk, shock = load_pair_config()
        for p in plans:
            self.assertAlmostEqual(pair_lower(p, risk, shock), interval_bounds(p, risk, shock)['lower'], places=12)
            values = [pair_lower(p, risk, shock, float(t)) for t in np.linspace(0, min(p.q1.upper, p.q2.upper), 101)]
            self.assertTrue(all(b >= a-1e-12 for a, b in zip(values, values[1:])))
        self.assertEqual(choose_pair(plans, risk, shock, cfg['floors'], cfg['target']).name, 'B')
        self.assertEqual(choose_pair(plans, risk, shock, {p.name: .65 for p in plans}, cfg['target']).name, 'A')

    def test_minimum_threshold_and_no_gain_region(self):
        _, plans, risk, shock = load_pair_config()
        p = plans[1]
        threshold = required_pair_floor(p, risk, shock)
        self.assertAlmostEqual(threshold, 4/7, places=12)
        self.assertAlmostEqual(pair_lower(p, risk, shock, threshold), .85)
        self.assertLess(pair_lower(p, risk, shock, threshold-1e-5), .85)
        self.assertAlmostEqual(pair_lower(p, risk, shock, .55), pair_lower(p, risk, shock, 0))
        self.assertEqual(required_pair_floor(plans[2], risk, shock), 0)
        self.assertAlmostEqual(pair_lower(p, risk, shock, .65), .8665)

    def test_infeasibility_and_zero_shock(self):
        _, plans, risk, shock = load_pair_config()
        with self.assertRaises(ValueError):
            required_pair_floor(plans[0], risk, shock, .97)
        with self.assertRaises(ValueError):
            required_pair_floor(plans[1], PI(.4, .5), PI(0, 0), .85)
        self.assertEqual(required_pair_floor(plans[1], PI(1, 1), PI(0, 0), .85), 0)
        with self.assertRaises(ValueError):
            choose_pair(plans, risk, shock, {p.name: 0 for p in plans}, .97)
        with self.assertRaises(ValueError):
            lp_pair(plans[1], risk, shock, .99)

    def test_invalid_inputs_and_ties(self):
        _, plans, risk, shock = load_pair_config()
        for floor in (-.1, .99, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                pair_lower(plans[1], risk, shock, floor)
        for target in (-.1, 1.1, float('nan')):
            with self.assertRaises(ValueError):
                required_pair_floor(plans[1], risk, shock, target)
        for menu, floors, target in (([], {}, .85), ([plans[0], plans[0]], {'A': 0}, .85),
                                     (plans, {}, .85), (plans, {p.name: 0 for p in plans}, float('nan'))):
            with self.assertRaises(ValueError):
                choose_pair(menu, risk, shock, floors, target)
        q = PI(1, 1)
        tied = [IntervalPlan('b', q, q, 1), IntervalPlan('a', q, q, 1)]
        self.assertEqual(choose_pair(tied, q, q, {'a': 0, 'b': 0}).name, 'a')

    def test_asymmetric_box_and_configurable_target(self):
        p = IntervalPlan('custom', PI(.4, .9), PI(.6, .7), 1)
        risk, shock = PI(.8, .95), PI(.1, .4)
        for floor in (0, .3, .7):
            self.assertAlmostEqual(pair_lower(p, risk, shock, floor), lp_pair(p, risk, shock, floor)[0])
        threshold = required_pair_floor(p, risk, shock, .65)
        self.assertAlmostEqual(pair_lower(p, risk, shock, threshold), .65)
