import importlib.util
from pathlib import Path
import sys
import unittest
spec=importlib.util.spec_from_file_location("risk_models",Path(__file__).resolve().parents[1]/"src"/"risk_models.py")
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)
class ModelTests(unittest.TestCase):
    def test_var_es(self):
        self.assertEqual(m.empirical_var_es([5,1,4,3,2],.8),{"var":4.0,"es":4.5})
    def test_finance(self):
        r=m.project_finance([120,120],[100,100],200,0)
        self.assertEqual(r["dscr"],[1.2,1.2])
        self.assertEqual(r["llcr"],1.2)
    def test_cpm(self):
        r=m.critical_path({"a":2,"b":3,"c":4},{"b":["a"],"c":["a"]})
        self.assertEqual(r["project_duration"],6)
        with self.assertRaises(ValueError): m.critical_path({"a":1},{"a":["a"]})
    def test_schedule_reproducible(self):
        a=m.schedule_monte_carlo({"a":(1,2,3)}, {}, 30, 1)
        self.assertEqual(a,m.schedule_monte_carlo({"a":(1,2,3)}, {}, 30, 1))
    def test_credit_portfolio_extremes(self):
        r=m.correlated_project_losses([100],[1],[0.5],50,seed=1)
        self.assertEqual(r["expected_loss"],50)
        self.assertEqual(r["es95"],50)
        r=m.correlated_project_losses([100],[0],[0.5],50,seed=1)
        self.assertEqual(r["expected_loss"],0)
if __name__=="__main__": unittest.main()
