import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from macro_lakehouse import VintageStore

class Tests(unittest.TestCase):
    def test_vintage_no_lookahead(self):
        store=VintageStore()
        store.ingest("CPI","2026-01-01","2026-02-01",3.0)
        store.ingest("CPI","2026-01-01","2026-03-01",3.2)
        self.assertEqual(store.as_of("CPI","2026-02-15"),[("2026-01-01",3.0)])
        self.assertEqual(store.as_of("CPI","2026-03-15"),[("2026-01-01",3.2)])
        self.assertEqual(store.as_of("CPI","2026-01-15"),[])
        store.close()
    def test_invalid_release(self):
        store=VintageStore()
        with self.assertRaises(ValueError):
            store.ingest("X","2026-02-01","2026-01-01",1)
        store.close()
if __name__=="__main__": unittest.main()
