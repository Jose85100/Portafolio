"""Smoke and invariants for 05-causal-ai-and-decision-intelligence/01-off-policy-policy-evaluation."""
import importlib.util
import pathlib
import unittest

PATH=pathlib.Path(__file__).resolve().parents[1]/"src"/"model.py"
spec=importlib.util.spec_from_file_location("project_model",PATH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestModel(unittest.TestCase):
    def test_core_behavior(self):
        rows=[{"context":0,"action":1,"propensity":0.5,"reward":1.0}]*4;r=mod.evaluate(rows,lambda c,a:0.5);self.assertEqual(r["ips"],1);self.assertEqual(r["effective_sample_size"],4)

if __name__=="__main__": unittest.main()
