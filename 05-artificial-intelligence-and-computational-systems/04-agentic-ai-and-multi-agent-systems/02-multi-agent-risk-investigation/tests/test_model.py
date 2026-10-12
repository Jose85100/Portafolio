"""Smoke and invariants for 04-agentic-ai-and-multi-agent-systems/02-multi-agent-risk-investigation."""
import importlib.util
import pathlib
import unittest

PATH=pathlib.Path(__file__).resolve().parents[1]/"src"/"model.py"
spec=importlib.util.spec_from_file_location("project_model",PATH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestModel(unittest.TestCase):
    def test_core_behavior(self):
        a={"id":"c"};a=mod.transition(a,"triaged",{"id":"bot","role":"agent"});self.assertEqual(a["state"],"triaged");self.assertRaises(PermissionError,mod.transition,{"state":"review"},"approved",{"id":"bot","role":"agent"})

if __name__=="__main__": unittest.main()
