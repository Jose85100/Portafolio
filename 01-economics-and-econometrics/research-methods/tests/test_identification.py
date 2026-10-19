import importlib.util
from pathlib import Path
import sys
import unittest
spec=importlib.util.spec_from_file_location("econ_identification",Path(__file__).resolve().parents[1]/"src"/"identification.py")
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)

class IdentificationTests(unittest.TestCase):
    def test_ols_exact_linear(self):
        x=[1,2,3,4,5]
        self.assertAlmostEqual(m.ols_slope([7-2*v for v in x],x),-2)
    def test_iv_exact_linear(self):
        x=[1,2,3,4,5];z=[1,1,2,3,5]
        self.assertAlmostEqual(m.iv_slope([7-2*v for v in x],x,z),-2)
    def test_shift_invariance(self):
        x=[1,2,4,8,16];y=[3,1,4,1,5]
        self.assertAlmostEqual(m.ols_slope(y,x),m.ols_slope([a+17 for a in y],[b+11 for b in x]))
    def test_reproducible(self):
        self.assertEqual(m.generate_endogenous_dgp(n=20,seed=3),m.generate_endogenous_dgp(n=20,seed=3))
    def test_endogeneity_bias(self):
        d=m.generate_endogenous_dgp(n=12000,seed=5)
        truth=d["true_beta"]
        ols=m.ols_slope(d["y"],d["x"])
        iv=m.iv_slope(d["y"],d["x"],d["z"])
        self.assertLess(abs(iv-truth),.08)
        self.assertGreater(abs(ols-truth),.15)
        self.assertLess(abs(ols-m.analytical_ols_probability_limit(truth,.8,1)),.05)
    def test_weak_instrument_rejection(self):
        with self.assertRaises(ValueError):m.iv_slope([1,2,3],[2,3,4],[1,1,1])
    def test_nonfinite(self):
        with self.assertRaises(ValueError):m.ols_slope([1,2,float("nan")],[1,2,3])

if __name__=="__main__":unittest.main()
