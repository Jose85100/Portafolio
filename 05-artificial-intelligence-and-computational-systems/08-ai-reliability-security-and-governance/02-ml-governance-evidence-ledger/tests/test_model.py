"""Smoke and invariants for 08-ai-reliability-security-and-governance/02-ml-governance-evidence-ledger."""
import importlib.util
import pathlib
import unittest

PATH=pathlib.Path(__file__).resolve().parents[1]/"src"/"model.py"
spec=importlib.util.spec_from_file_location("project_model",PATH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestModel(unittest.TestCase):
    def test_core_behavior(self):
        a=mod.append([],{"model":"v1"});self.assertTrue(mod.verify(a));a[0]["payload"]["model"]="v2";self.assertFalse(mod.verify(a))

if __name__=="__main__": unittest.main()
