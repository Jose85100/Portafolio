import importlib.util
from pathlib import Path
import sys
import unittest
from math import exp, isinf, sqrt

spec=importlib.util.spec_from_file_location("numerical_core",Path(__file__).resolve().parents[1]/"src"/"numerical_core.py")
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)

class Invariants(unittest.TestCase):
    def test_quantile_monotonic(self):
        x=[4,1,5,2,3]
        self.assertEqual([m.quantile(x,p) for p in (.2,.4,.6,.8,1)],[1,2,3,4,5])
        self.assertEqual(m.expected_shortfall(x,.8),4.5)
    def test_wasserstein_metric_basics(self):
        self.assertEqual(m.wasserstein_1d([1,2,3],[3,2,1]),0)
        self.assertEqual(m.wasserstein_1d([1,2],[4,5]),3)
        self.assertAlmostEqual(m.wasserstein_1d([0,2],[1,3]),1)
        with self.assertRaises(ValueError): m.wasserstein_1d([1],[1,2])
    def test_kl_nonnegative_and_boundary(self):
        for p,q in ((.2,.4),(.5,.5),(0,.1),(1,.8)):
            self.assertGreaterEqual(m.kl_bernoulli(p,q),-1e-14)
        self.assertEqual(m.kl_bernoulli(.5,.5),0)
        self.assertTrue(isinf(m.kl_bernoulli(.1,0)))
    def test_bs_limits(self):
        self.assertAlmostEqual(m.bs_call(100,100,0,0,1),0)
        self.assertAlmostEqual(m.bs_call(100,90,.05,0,1),100-90*exp(-.05))
        self.assertAlmostEqual(m.bs_call(100,100,.05,.2,1),10.450583572185565,places=8)
    def test_sde_deterministic_order(self):
        exact=100*exp(.1)
        errors=[]
        for steps in (10,20,40,80):
            terminal=m.euler_maruyama_gbm(100,.1,0,1,steps,paths=1)[0]
            errors.append(abs(terminal-exact))
        self.assertTrue(all(a>b for a,b in zip(errors,errors[1:])))
    def test_sde_seed(self):
        a=m.euler_maruyama_gbm(100,.05,.2,1,16,paths=20,seed=7)
        self.assertEqual(a,m.euler_maruyama_gbm(100,.05,.2,1,16,paths=20,seed=7))
    def test_mc_vs_bs_confidence(self):
        result=m.mc_call(100,100,.05,.2,1,paths=25000,seed=42)
        benchmark=m.bs_call(100,100,.05,.2,1)
        self.assertLess(abs(result["price"]-benchmark),4*result["standard_error"])
    def test_reject_nonfinite(self):
        with self.assertRaises(ValueError): m.quantile([1,float("nan")],.5)
        with self.assertRaises(ValueError): m.euler_maruyama_gbm(100,0,-1,1,10)

if __name__=="__main__":unittest.main()
