"""Smoke and invariants for 06-knowledge-engineering-and-rag/01-temporal-regulatory-graphrag."""
import importlib.util
import pathlib
import unittest

PATH=pathlib.Path(__file__).resolve().parents[1]/"src"/"model.py"
spec=importlib.util.spec_from_file_location("project_model",PATH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestModel(unittest.TestCase):
    def test_core_behavior(self):
        r=mod.retrieve([{"id":"r","valid_from":"2025-01-01","published_at":"2025-01-01","text":"credit risk","source":"official"}],"2026-01-01","credit");self.assertEqual(r[0]["id"],"r")

if __name__=="__main__": unittest.main()
