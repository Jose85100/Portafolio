import csv
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from risk_data_platform import build_snapshot, publish_atomic

class Tests(unittest.TestCase):
    def test_snapshot_and_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp)/"loans.csv"
            src.write_text("loan_id,as_of_date,principal,days_past_due\na,2026-01-01,100,0\na,2026-01-02,80,5\nb,2026-01-02,20,31\n")
            x = build_snapshot(src, "2026-01-02")
            self.assertEqual(x["loan_count"], 2)
            self.assertEqual(x["principal_total"], "100")
            publish_atomic(x, Path(tmp)/"out.json")
            self.assertTrue((Path(tmp)/"out.json").exists())
    def test_conflicting_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"x.csv"
            p.write_text("loan_id,as_of_date,principal,days_past_due\na,2026-01-01,1,0\na,2026-01-01,2,0\n")
            with self.assertRaises(ValueError): build_snapshot(p,"2026-01-02")
if __name__=="__main__": unittest.main()
