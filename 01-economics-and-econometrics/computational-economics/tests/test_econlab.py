import unittest
import importlib.util
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"src"/"econlab.py"
spec=importlib.util.spec_from_file_location("econlab",p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class EconLabTests(unittest.TestCase):
    def test_ols_exact(self):
        self.assertAlmostEqual(m.ols([1,2,3,4],[3,5,7,9])[1],2)
    def test_ols_degenerate(self):
        with self.assertRaises(ValueError): m.ols([1,1,1],[2,3,4])
    def test_simulation_reproducible(self):
        self.assertEqual(m.generate_panel(seed=2),m.generate_panel(seed=2))
    def test_bootstrap_interval(self):
        # Nominal 95% intervals need not cover in every finite sample.
        covered = 0
        for seed in range(100):
            x,y=m.generate_panel(n=200,noise=.1,seed=seed)
            lo,hi=m.bootstrap_slope(x,y,seed=seed+1000)
            self.assertLessEqual(lo,hi)
            covered += lo <= .8 <= hi
        # Broad Monte Carlo guardrail, not a theorem of exact coverage.
        self.assertGreaterEqual(covered,85)
    def test_credit_loss(self):
        self.assertAlmostEqual(m.expected_credit_loss([.1,.2],[.5,.5],[100,200]),25)
    def test_credit_loss_validation(self):
        with self.assertRaises(ValueError): m.expected_credit_loss([1.1],[.5],[100])
    def test_markov_conservation(self):
        v=m.markov_step([.5,.5],[[.8,.2],[.1,.9]])
        self.assertAlmostEqual(sum(v),1)
        self.assertAlmostEqual(v[0],.45)
    def test_best_response(self):
        self.assertEqual(m.best_response_grid(lambda a:-(a-2)**2,range(5)),2)
if __name__=="__main__": unittest.main()
