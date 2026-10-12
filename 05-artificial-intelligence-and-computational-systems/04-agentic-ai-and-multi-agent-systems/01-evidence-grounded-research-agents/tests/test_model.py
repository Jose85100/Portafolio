"""Smoke and invariants for 04-agentic-ai-and-multi-agent-systems/01-evidence-grounded-research-agents."""
import importlib.util
import pathlib
import unittest

PATH=pathlib.Path(__file__).resolve().parents[1]/"src"/"model.py"
spec=importlib.util.spec_from_file_location("project_model",PATH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestModel(unittest.TestCase):
    def test_core_behavior(self):
        a=mod.audit_claims([{"claim":"x","evidence_ids":["d"]}],[{"id":"d","verified":True}]);self.assertEqual(mod.coverage(a),1.0)

if __name__=="__main__": unittest.main()
