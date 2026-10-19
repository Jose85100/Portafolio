import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

path=Path(__file__).resolve().parents[1]/"review.py"
spec=importlib.util.spec_from_file_location("econ_review",path)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ReviewTests(unittest.TestCase):
    def test_invalid_notebook(self):
        with TemporaryDirectory() as d:
            p=Path(d)/"bad.ipynb";p.write_text("{bad",encoding="utf-8")
            self.assertFalse(m.notebook_evidence(p)["valid"])
    def test_valid_notebook(self):
        with TemporaryDirectory() as d:
            p=Path(d)/"ok.ipynb"
            p.write_text(json.dumps({"cells":[{"cell_type":"markdown","source":["Contraejemplo"]},
             {"cell_type":"code","source":["from random import Random\nrng=Random(42)\nassert 1==1\nplt.plot([1])"]}]}),encoding="utf-8")
            ev=m.notebook_evidence(p)
            self.assertTrue(ev["has_fixed_seed"])
            self.assertTrue(ev["has_counterexample"])
            self.assertTrue(ev["has_assert"])
            self.assertTrue(ev["has_plot"])
    def test_missing_identification(self):
        with TemporaryDirectory() as d:
            p=Path(d)/"project";p.mkdir();(p/"README.md").write_text("# Minimal",encoding="utf-8")
            codes={x["code"] for x in m.review_project(p)}
            self.assertIn("no_falsification",codes)
            self.assertIn("no_executable",codes)
    def test_audit_scope(self):
        with TemporaryDirectory() as d:
            root=Path(d);area=root/"01-macroeconomics";area.mkdir()
            project=area/"example";project.mkdir()
            (project/"README.md").write_text("# Test",encoding="utf-8")
            result=m.audit(root)
            self.assertEqual(result["projects_reviewed"],1)
            self.assertEqual(result["projects"][0]["project"],"01-macroeconomics/example")
if __name__=="__main__":unittest.main()
