import sys
import unittest
from pathlib import Path
from dataclasses import replace
from hypothesis import given, settings, strategies as st
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.vintages import Release, snapshot

class LedgerProperties(unittest.TestCase):
    @settings(max_examples=100,derandomize=True)
    @given(st.lists(st.tuples(st.integers(0,30),st.integers(0,10),
           st.floats(-1e5,1e5,allow_nan=False,allow_infinity=False)),max_size=50),st.integers(0,40))
    def test_asof_future_mutation_and_order(self, values, origin):
        # Distinct event keys exclude ambiguous duplicate timestamps.
        rows=[Release(str(i),event,event+lag,value,False)
              for i,(event,lag,value) in enumerate(values)]
        changed=[replace(r,value=r.value+1e6) if r.available>origin else r for r in rows]
        self.assertEqual(snapshot(rows,origin),snapshot(changed,origin))
        self.assertEqual(snapshot(rows,origin),snapshot(list(reversed(rows)),origin))
        self.assertTrue(all(r.available<=origin for r in snapshot(rows,origin).values()))
