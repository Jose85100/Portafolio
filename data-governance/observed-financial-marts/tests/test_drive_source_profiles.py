import importlib.util
import pathlib
import sqlite3
import tempfile
import unittest

BASE = pathlib.Path(__file__).resolve().parents[1] / "src"


def load(name):
    path = BASE / (name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CanonicalDataTests(unittest.TestCase):
    def test_drive_rejects_unapproved_sources(self):
        module = load("drive_readonly")
        with self.assertRaisesRegex(ValueError, "Unapproved"):
            module.download("unlisted_id", "/tmp", token="fake")

    def test_drive_requires_authorization(self):
        module = load("drive_readonly")
        # Check caller can only select allowlisted named sources.
        self.assertIn("sfc_credit_product", module.APPROVED)

    def test_sfc_detects_conflicting_duplicates(self):
        import csv
        module = load("sfc_product_profile")
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "source.csv"
            columns = list(module.KEY) + ["DESCRIP_UC", module.BALANCE, module.CURRENT]
            data = [
                ["1","12","31/01/2025","2","5","CONSUMO","100","80"],
                ["1","12","31/01/2025","2","5","CONSUMO","110","80"],
            ]
            with p.open("w",newline="") as f:
                writer=csv.writer(f);writer.writerow(columns);writer.writerows(data)
            report=module.inspect(p)
            self.assertEqual(report["rows"],2)
            self.assertEqual(report["duplicate_business_keys"],1)
            self.assertEqual(report["conflicting_duplicate_keys"],1)

    def test_market_profile_with_real_schema_fixture(self):
        module=load("market_sqlite_profile")
        with tempfile.TemporaryDirectory() as td:
            path=pathlib.Path(td)/"market.sqlite"
            with sqlite3.connect(path) as db:
                db.execute("CREATE TABLE prices (symbol text,date text,open real,high real,low real,close real,adjusted_close real)")
                db.execute("CREATE TABLE macro_observations (indicator text,date text,value real)")
                db.executemany("INSERT INTO prices VALUES ('SPY',?,?,?,?,?,?)",
                               [(f"2025-01-{i+1:02d}",100+i,101+i,99+i,100+i,100+i)
                                for i in range(30)])
            report=module.inspect(path)
            self.assertEqual(report["prices_rows"],30)
            self.assertEqual(report["ohlc_inconsistencies"],0)
            self.assertEqual(report["per_symbol"][0]["status"],"DESCRIPTIVE_NOT_BACKTESTED")


if __name__ == "__main__":
    unittest.main()
