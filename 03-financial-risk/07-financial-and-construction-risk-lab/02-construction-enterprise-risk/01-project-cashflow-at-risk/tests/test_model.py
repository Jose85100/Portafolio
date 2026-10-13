import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('construction_cashflow', Path(__file__).resolve().parents[1] / 'src' / 'model.py')
module = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = module
spec.loader.exec_module(module)

class CashflowTests(unittest.TestCase):
    def setUp(self):
        self.project = module.Project(100, (80, 80), (60, 60), (10, 10))

    def test_deterministic_path(self):
        result = module.simulate(self.project, scenarios=100, collection_vol=0, cost_vol=0)
        self.assertEqual(result['probability_shortfall'], 0)
        self.assertEqual(result['mean_terminal_cash'], 120)

    def test_seed_reproducibility(self):
        self.assertEqual(module.simulate(self.project, scenarios=50, seed=7), module.simulate(self.project, scenarios=50, seed=7))

    def test_certain_shortfall(self):
        p = module.Project(0, (0,), (100,), (0,))
        r = module.simulate(p, scenarios=10, collection_vol=0, cost_vol=0)
        self.assertEqual(r['peak_shortfall_q95'], 100)
        self.assertEqual(r['probability_shortfall'], 1)

    def test_bad_inputs(self):
        with self.assertRaises(ValueError):
            module.Project(0, (1,), (1, 2), (0,))
        with self.assertRaises(ValueError):
            module.simulate(self.project, scenarios=0)

if __name__ == '__main__':
    unittest.main()
