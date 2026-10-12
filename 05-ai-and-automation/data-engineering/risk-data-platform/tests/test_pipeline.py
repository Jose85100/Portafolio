import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pipeline import normalize, run

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "input.csv"
        self.output = self.root / "curated.csv"
        self.manifest = self.root / "manifest.json"

    def write(self, lines):
        self.source.write_text("loan_id,as_of_date,principal,days_past_due,status\n" + lines, encoding="utf-8")

    def test_initial_and_idempotent_replay(self):
        self.write("A,2026-10-01,100.25,0,active\nB,2026-10-01,0,0,closed\n")
        first = run(self.source, self.output, self.manifest)
        original = self.output.read_bytes()
        second = run(self.source, self.output, self.manifest)
        self.assertEqual(original, self.output.read_bytes())
        self.assertEqual(first["sha256"], second["sha256"])
        self.assertEqual(second["new_keys"], 0)
        self.assertEqual(second["total_principal"], "100.25")

    def test_incremental_upsert_and_historical_snapshot(self):
        self.write("A,2026-10-01,100,0,active\n")
        run(self.source, self.output, self.manifest)
        self.write("A,2026-10-02,95,1,active\n")
        result = run(self.source, self.output, self.manifest)
        self.assertEqual(result["published_rows"], 2)
        self.assertEqual(result["total_principal"], "195.00")

    def test_conflict_rejects_without_mutation(self):
        self.write("A,2026-10-01,100,0,active\n")
        run(self.source, self.output, self.manifest)
        before = self.output.read_bytes()
        self.write("A,2026-10-02,100,0,active\nA,2026-10-02,200,0,active\n")
        with self.assertRaises(ValueError):
            run(self.source, self.output, self.manifest, self.root / "rejects.json")
        self.assertEqual(before, self.output.read_bytes())
        self.assertTrue((self.root / "rejects.json").exists())

    def test_invalid_schema_and_financial_rules(self):
        self.write("A,2026-10-01,100,0,closed\n")
        with self.assertRaises(ValueError):
            run(self.source, self.output, self.manifest)
        with self.assertRaises(ValueError):
            normalize({"loan_id":"A","as_of_date":"2026-10-01",
                       "principal":"NaN","days_past_due":"0","status":"active"})

    def test_reconciled_manifest_hash(self):
        self.write("A,2026-10-01,100,0,active\n")
        result = run(self.source, self.output, self.manifest)
        self.assertEqual(result, json.loads(self.manifest.read_text()))

if __name__ == "__main__":
    unittest.main()
