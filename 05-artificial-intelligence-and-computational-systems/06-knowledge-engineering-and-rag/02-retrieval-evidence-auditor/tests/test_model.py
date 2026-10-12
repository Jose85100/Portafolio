"""Smoke and invariants for 06-knowledge-engineering-and-rag/02-retrieval-evidence-auditor."""
import importlib.util
import pathlib
import unittest

PATH=pathlib.Path(__file__).resolve().parents[1]/"src"/"model.py"
spec=importlib.util.spec_from_file_location("project_model",PATH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestModel(unittest.TestCase):
    def test_core_behavior(self):
        r=mod.verify([{"document_id":"a","quote":"abc"}],[{"id":"a","text":"x abc y","published_at":"2025-01-01"}],"2026-01-01");self.assertTrue(r[0]["verified"])

if __name__=="__main__": unittest.main()
