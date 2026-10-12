"""Smoke and invariants for 02-machine-learning-engineering/02-conformal-risk-prediction."""
import importlib.util
import pathlib
import unittest

PATH=pathlib.Path(__file__).resolve().parents[1]/"src"/"model.py"
spec=importlib.util.spec_from_file_location("project_model",PATH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestModel(unittest.TestCase):
    def test_core_behavior(self):
        q=mod.fit_intervals([1,2,3,4,5,6,7,8,9,10],[1]*10,0.2);self.assertEqual(q,8);self.assertEqual(len(mod.predict_intervals([2,3],q)),2)

if __name__=="__main__": unittest.main()
