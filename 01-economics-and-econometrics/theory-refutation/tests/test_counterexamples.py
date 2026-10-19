import importlib.util
from pathlib import Path
import sys
import unittest
p=Path(__file__).resolve().parents[1]/"src"/"counterexamples.py"
s=importlib.util.spec_from_file_location("counterexamples",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class RefutationTests(unittest.TestCase):
    def test_did_identification_when_parallel(self):
        x=m.did_counterexample(n=15000,differential_trend=0,seed=1)
        self.assertLess(abs(x["estimate"]-x["true_att"]),.05)
    def test_did_counterexample(self):
        x=m.did_counterexample(n=15000,differential_trend=1.5,seed=1)
        self.assertLess(abs(x["estimate"]-3.5),.05)
        self.assertGreater(abs(x["estimate"]-x["true_att"]),1.3)
    def test_phillips_exogenous(self):
        x=m.phillips_policy_counterexample(n=15000,feedback=0,seed=1)
        self.assertLess(abs(x["estimate"]-.3),.05)
    def test_phillips_sign_reversal(self):
        x=m.phillips_policy_counterexample(n=15000,feedback=1,seed=1)
        self.assertLess(abs(x["estimate"]-x["population_ols"]),.05)
        self.assertLess(x["estimate"],0)
    def test_el_identity(self):
        self.assertAlmostEqual(m.expected_loss([.1,.2],[.5,.4],[100,200]),21)
    def test_dependence_changes_joint_default(self):
        a=m.portfolio_loss_tail(n=30000,common_factor_loading=0,seed=1)
        b=m.portfolio_loss_tail(n=30000,common_factor_loading=.8,seed=1)
        self.assertAlmostEqual(a["mean_loss"],20,delta=1)
        self.assertAlmostEqual(b["mean_loss"],20,delta=1)
        self.assertGreater(b["joint_default_probability"],a["joint_default_probability"]+.025)
    def test_invalid_pd(self):
        with self.assertRaises(ValueError):m.expected_loss([1.1],[.5],[100])
if __name__=="__main__":unittest.main()
