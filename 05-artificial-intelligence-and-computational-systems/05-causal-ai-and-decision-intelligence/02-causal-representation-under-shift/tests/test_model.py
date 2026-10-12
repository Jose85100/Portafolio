"""Smoke and invariants for 05-causal-ai-and-decision-intelligence/02-causal-representation-under-shift."""
import importlib.util
import pathlib
import unittest

PATH=pathlib.Path(__file__).resolve().parents[1]/"src"/"model.py"
spec=importlib.util.spec_from_file_location("project_model",PATH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestModel(unittest.TestCase):
    def test_core_behavior(self):
        r=mod.environment_risk([{"environment":"a","features":1,"target":1},{"environment":"b","features":1,"target":3}],lambda x:x);self.assertEqual(r["risk_gap"],4)

if __name__=="__main__": unittest.main()
