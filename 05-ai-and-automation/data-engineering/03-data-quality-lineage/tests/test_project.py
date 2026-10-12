import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from quality_lineage import validate_csv,evidence

class Tests(unittest.TestCase):
    def test_rules_and_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"data.csv"
            p.write_text("id,amount\na,10\na,-1\n")
            result=validate_csv(p,[{"field":"id","op":"unique"},{"field":"amount","op":"min","value":0}])
            self.assertFalse(result["passed"])
            self.assertEqual(len(result["violations"]),2)
            self.assertEqual(len(evidence(p,result)["sha256"]),64)
    def test_missing_column(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"data.csv"
            p.write_text("id\na\n")
            with self.assertRaises(ValueError):
                validate_csv(p,[{"field":"unknown","op":"not_null"}])
if __name__=="__main__": unittest.main()
