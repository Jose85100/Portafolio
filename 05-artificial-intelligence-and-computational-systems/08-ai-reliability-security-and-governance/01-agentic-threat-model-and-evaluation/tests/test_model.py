"""Smoke and invariants for 08-ai-reliability-security-and-governance/01-agentic-threat-model-and-evaluation."""
import importlib.util
import pathlib
import unittest

PATH=pathlib.Path(__file__).resolve().parents[1]/"src"/"model.py"
spec=importlib.util.spec_from_file_location("project_model",PATH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestModel(unittest.TestCase):
    def test_core_behavior(self):
        p={"analyst":[{"tool":"read","resource":"risk"}]};self.assertTrue(mod.authorize({"role":"analyst"},"read","risk",p));self.assertFalse(mod.authorize({"role":"analyst"},"write","risk",p))

if __name__=="__main__": unittest.main()
