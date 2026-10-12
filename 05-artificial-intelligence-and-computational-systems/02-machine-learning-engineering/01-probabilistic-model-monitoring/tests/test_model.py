"""Smoke and invariants for 02-machine-learning-engineering/01-probabilistic-model-monitoring."""
import importlib.util
import pathlib
import unittest

PATH=pathlib.Path(__file__).resolve().parents[1]/"src"/"model.py"
spec=importlib.util.spec_from_file_location("project_model",PATH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestModel(unittest.TestCase):
    def test_core_behavior(self):
        r=mod.monitor([0]*80+[1]*20,[0]*50+[1]*50);self.assertTrue(r["alert"]);self.assertGreater(r["delta"],0)

if __name__=="__main__": unittest.main()
