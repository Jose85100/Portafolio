import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from quant_data_factory import build_features,temporal_split

class Tests(unittest.TestCase):
    def test_feature_and_purging(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"prices.csv"
            p.write_text("asset,date,price\n"+ "".join(f"A,2026-01-{i:02d},{100+i}\n" for i in range(1,10)))
            rows=build_features(p,lookback=2,horizon=2)
            self.assertEqual(len(rows),5)
            train,test=temporal_split(rows,"2026-01-05","2026-01-07")
            self.assertTrue(all(r["target_end"]<"2026-01-07" for r in train))
            self.assertTrue(all(r["feature_date"]>="2026-01-07" for r in test))
    def test_bad_horizon(self):
        with self.assertRaises(ValueError): build_features("ignored",horizon=0)
if __name__=="__main__": unittest.main()
