import sys,importlib.util,csv,math
from pathlib import Path
import unittest
root=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('risk_contract_model',root/'python/src/risk_models.py')
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class ModelContractTests(unittest.TestCase):
    def test_fractional_es_hinge_fixtures(self):
        with (root/'tests/fixtures/tail_contract.csv').open() as handle:
            for row in csv.DictReader(handle):
                losses=list(map(float,row['losses'].split(';')));result=m.empirical_var_es(losses,float(row['alpha']))
                self.assertEqual(result['var'],float(row['var']))
                self.assertAlmostEqual(result['es'],float(row['es']),places=9)
    def test_nonfinite_losses_and_schedule(self):
        for value in [math.nan,math.inf,-math.inf]:
            with self.assertRaises(ValueError):m.empirical_var_es([1,value])
            with self.assertRaises(ValueError):m.critical_path({'a':value},{})
            with self.assertRaises(ValueError):m.project_finance([value],[1],1)
    def test_zero_service_and_negative_cfads(self):
        result=m.project_finance([-10,20],[5,0],10,0)
        self.assertEqual(result['dscr'],[-2.,None]);self.assertEqual(result['minimum_dscr'],-2.)
        self.assertEqual(result['llcr'],1.)
    def test_bad_counts_and_portfolio(self):
        for count in [0,True,1.5]:
            with self.assertRaises(ValueError):m.schedule_monte_carlo({'a':(1,2,3)},{},n=count)
            with self.assertRaises(ValueError):m.correlated_project_losses([1],[.1],[.5],scenarios=count)
        with self.assertRaises(ValueError):m.correlated_project_losses([math.inf],[.1],[.5])
    def test_atom_splitting_and_translation(self):
        original=m.empirical_var_es([0,1,10],.8)['es']
        duplicated=m.empirical_var_es([0,0,1,1,10,10],.8)['es']
        shifted=m.empirical_var_es([5,6,15],.8)['es']
        self.assertAlmostEqual(original,duplicated);self.assertAlmostEqual(shifted,original+5)
