import sys
import unittest
from pathlib import Path
from hypothesis import given, settings, strategies as st
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.game import Game, equilibria, exact_equilibria, gain, iterate, outcomes, posterior, regret

class GameTests(unittest.TestCase):
    def test_main_three_equilibria(self):
        expected=[((0,0),(0,0)),((0,1),(0,1)),((1,1),(1,1))]
        self.assertEqual(equilibria(Game()),expected)
        self.assertEqual(exact_equilibria(Game()),expected)
    def test_zero_complementarity_unique(self):
        self.assertEqual(equilibria(Game(complementarity=0)),[((0,0),(0,0))])
    def test_posterior_bayes(self):
        self.assertAlmostEqual(posterior(Game(),1),.8)
        self.assertAlmostEqual(posterior(Game(),0),.2)
    def test_extreme_cost(self):
        self.assertEqual(equilibria(Game(cost=3)),[((0,0),(0,0))])
        self.assertEqual(equilibria(Game(cost=0)),[((1,1),(1,1))])
    def test_outcomes(self):
        high=outcomes(Game(),((0,1),(0,1)))
        self.assertAlmostEqual(high['freeze_given_good'],.04)
        self.assertAlmostEqual(high['lender_payoff'],.444)
        self.assertAlmostEqual(high['lending_rate'],.5)
    def test_baseline_start_dependence(self):
        g=Game()
        self.assertEqual(iterate(g)[0],((0,0),(0,0)))
        self.assertEqual(iterate(g,((1,1),(1,1)))[0],((1,1),(1,1)))
    def test_synchronous_cycle(self):
        self.assertIsNone(iterate(Game(),((0,0),(1,1)))[0])
    def test_invalid(self):
        for kwargs in ({'prior':0},{'accuracy':.4},{'cost':-1},{'complementarity':-1},{'cost':float('nan')}):
            with self.assertRaises(ValueError): Game(**kwargs)
        with self.assertRaises(ValueError): posterior(Game(),2)
        with self.assertRaises(ValueError): equilibria(Game(),-1)
        with self.assertRaises(ValueError): iterate(Game(),limit=0)
    def test_limit(self):
        self.assertIsNone(iterate(Game(),((0,1),(1,0)),limit=1)[0])
    def test_tie_all_profiles(self):
        # Uninformative signals, zero externality, cost=prior: every action indifferent.
        g=Game(accuracy=.5,cost=.5,complementarity=0)
        self.assertEqual(len(equilibria(g)),16)
        self.assertEqual(equilibria(g),exact_equilibria(g))
    @settings(max_examples=100,derandomize=True,deadline=None)
    @given(st.integers(1,9),st.integers(5,10),st.integers(0,20),st.integers(0,15))
    def test_oracle_and_probability_properties(self,pi,q,c,a):
        g=Game(pi/10,q/10,c/10,a/10)
        self.assertEqual(equilibria(g),exact_equilibria(g))
        for profile in equilibria(g):
            self.assertLessEqual(regret(g,profile),1e-12)
            out=outcomes(g,profile)
            self.assertTrue(0<=out['freeze_given_good']<=1+1e-12)
            self.assertTrue(0<=out['lending_rate']<=1+1e-12)
    @settings(max_examples=100,derandomize=True)
    @given(st.floats(.01,.99),st.floats(.5,1),st.floats(0,2))
    def test_complementarity_monotone_gain(self,pi,q,c):
        low=Game(pi,q,c,0); high=Game(pi,q,c,1)
        for signal in (0,1):
            self.assertGreaterEqual(gain(high,signal,(0,1))+1e-14,gain(low,signal,(0,1)))

if __name__=='__main__': unittest.main()
