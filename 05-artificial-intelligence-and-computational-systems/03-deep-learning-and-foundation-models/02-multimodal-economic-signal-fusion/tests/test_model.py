"""Smoke and invariants for 03-deep-learning-and-foundation-models/02-multimodal-economic-signal-fusion."""
import importlib.util
import pathlib
import unittest

PATH=pathlib.Path(__file__).resolve().parents[1]/"src"/"model.py"
spec=importlib.util.spec_from_file_location("project_model",PATH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestModel(unittest.TestCase):
    def test_core_behavior(self):
        r=mod.fuse([{"decision_at":"2026-01-02T00:00:00Z"}],[{"channel":"text","available_at":"2026-01-03T00:00:00Z","value":9}]);self.assertIsNone(r[0]["text"])

if __name__=="__main__": unittest.main()
