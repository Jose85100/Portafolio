"""Smoke and invariants for 03-deep-learning-and-foundation-models/01-temporal-foundation-model-evaluation."""
import importlib.util
import pathlib
import unittest

PATH=pathlib.Path(__file__).resolve().parents[1]/"src"/"model.py"
spec=importlib.util.spec_from_file_location("project_model",PATH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestModel(unittest.TestCase):
    def test_core_behavior(self):
        r=mod.rolling_origin(list(range(10)),horizon=2,min_train=4);self.assertEqual(len(r["rows"]),5);self.assertEqual(r["rows"][0]["forecast"],3)

if __name__=="__main__": unittest.main()
