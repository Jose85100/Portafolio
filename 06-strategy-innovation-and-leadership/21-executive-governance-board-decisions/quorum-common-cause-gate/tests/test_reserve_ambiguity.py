import unittest
from src.reserve_ambiguity import ReservePlan,bounds,choose_plan,coupling,nominal_existing_engine,symmetric_threshold


class ReserveAmbiguityTests(unittest.TestCase):
    def test_lp_oracle_sharp_bounds(self):
        from scipy.optimize import linprog
        for q1,q2 in ((0,0),(1,1),(.7,.7),(.1,.8),(.8,.6)):
            p=ReservePlan('p',q1,q2,1)
            b=bounds(p)
            for sign,key in ((1,'lower_joint'),(-1,'upper_joint')):
                lp=linprog([0,0,0,sign],A_eq=[[1,1,1,1],[0,0,1,1],[0,1,0,1]],b_eq=[1,q1,q2],bounds=(0,None),method='highs')
                self.assertTrue(lp.success)
                self.assertAlmostEqual(sign*lp.fun,b[key],places=10)
                self.assertAlmostEqual(sum(coupling(p,b[key])),1)

    def test_existing29_engine_recovers_nominal(self):
        for q in (0,.7,.8,.9,1):
            p=ReservePlan('p',q,q,1)
            for shock in (0,.2,1):
                self.assertAlmostEqual(nominal_existing_engine(p,shock),bounds(p,shock)['nominal_availability'],places=12)

    def test_cheapest_false_pass_and_robust_choice(self):
        plans=[ReservePlan('a',.7,.7,2),ReservePlan('b',.8,.8,3),ReservePlan('c',.9,.9,4)]
        self.assertEqual(choose_plan(plans,robust=False)['name'],'a')
        self.assertEqual(choose_plan(plans)['name'],'b')
        self.assertLess(bounds(plans[0])['lower_availability'],.85)
        self.assertGreater(bounds(plans[0])['nominal_availability'],.85)
        with self.assertRaises(ValueError):
            choose_plan(plans,target=.97)

    def test_threshold_and_positive_dependence_counterexample(self):
        nominal,robust=symmetric_threshold()
        self.assertAlmostEqual(nominal,.6882472016116853)
        self.assertAlmostEqual(robust,.7368421052631577)
        p=ReservePlan('p',.7,.7,1)
        b=bounds(p)
        self.assertGreater(b['upper_availability'],b['nominal_availability'])
        self.assertEqual(symmetric_threshold(target=.5),(0,0))
        with self.assertRaises(ValueError):
            symmetric_threshold(target=.97)

    def test_invalid_and_coupling(self):
        for args in (('',.1,.2,1),('p',-1,.2,1),('p',.1,.2,-1)):
            with self.assertRaises(ValueError):
                ReservePlan(*args)
        p=ReservePlan('p',.7,.7,1)
        with self.assertRaises(ValueError):
            coupling(p,.2)
        with self.assertRaises(ValueError):
            bounds(p,shock=2)
        with self.assertRaises(ValueError):
            choose_plan([])
        with self.assertRaises(ValueError):
            symmetric_threshold(shock=0)
