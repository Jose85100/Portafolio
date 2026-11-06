import importlib.util
import json
import pathlib
import unittest

p = pathlib.Path(__file__).resolve().parents[1] / "tools" / "data_provenance_audit.py"
spec = importlib.util.spec_from_file_location("audit", p)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class InventoryTests(unittest.TestCase):
    def test_detect_synthetic(self):
        row = audit.classify(pathlib.Path("01-economics-and-econometrics/main.py"),
                             "x = np.random.normal(size=30)")
        self.assertEqual(row["audit_status"], "SYNTHETIC_CANDIDATE")
        self.assertEqual(row["verified_observed_integration"], "NOT_VERIFIED")

    def test_source_not_verified(self):
        row = audit.classify(pathlib.Path("03-financial-risk/source.py"),
                             "import requests; requests.get('https://www.datos.gov.co')")
        self.assertEqual(row["audit_status"], "EXTERNAL_SOURCE_CANDIDATE")
        self.assertEqual(row["verified_observed_integration"], "NOT_VERIFIED")

    def test_mixed(self):
        row = audit.classify(pathlib.Path("test.py"),
                             "a = np.random.uniform(size=3); b = pd.read_csv('real.csv')")
        self.assertEqual(row["audit_status"], "MIXED_REVIEW")

    def test_notebook_code_only(self):
        s = json.dumps({"cells": [
            {"cell_type": "markdown", "source": ["Datos sintéticos no aplican"]},
            {"cell_type": "code", "source": ["x = 1"]}]})
        self.assertEqual(audit.code_only(pathlib.Path("study.ipynb"), s), "x = 1")

    def test_notebook_generation(self):
        s = json.dumps({"cells": [{"cell_type": "code", "source": ["rng = np.random.default_rng(4)"]}]})
        code = audit.code_only(pathlib.Path("study.ipynb"), s)
        self.assertTrue(audit.classify(pathlib.Path("study.ipynb"), code)["synthetic_signal"])


if __name__ == "__main__":
    unittest.main()
