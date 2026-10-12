"""Smoke and invariants for 07-intelligent-automation-and-process-mining/02-verifiable-workflow-orchestration."""
import importlib.util
import pathlib
import unittest

PATH=pathlib.Path(__file__).resolve().parents[1]/"src"/"model.py"
spec=importlib.util.spec_from_file_location("project_model",PATH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestModel(unittest.TestCase):
    def test_core_behavior(self):
        e={"id":"1","type":"received"};a=mod.apply_event({},e);b=mod.apply_event(a,e);self.assertEqual(len(b["events"]),1);self.assertRaises(ValueError,mod.apply_event,a,{"id":"1","type":"other"})

if __name__=="__main__": unittest.main()
