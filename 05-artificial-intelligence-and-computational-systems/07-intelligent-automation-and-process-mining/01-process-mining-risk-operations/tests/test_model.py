"""Smoke and invariants for 07-intelligent-automation-and-process-mining/01-process-mining-risk-operations."""
import importlib.util
import pathlib
import unittest

PATH=pathlib.Path(__file__).resolve().parents[1]/"src"/"model.py"
spec=importlib.util.spec_from_file_location("project_model",PATH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestModel(unittest.TestCase):
    def test_core_behavior(self):
        r=mod.discover([{"case_id":"1","timestamp":"2026-01-01T00:00:00Z","activity":"start"},{"case_id":"1","timestamp":"2026-01-01T01:00:00Z","activity":"end"}]);self.assertEqual(r["mean_duration_seconds"],3600)

if __name__=="__main__": unittest.main()
