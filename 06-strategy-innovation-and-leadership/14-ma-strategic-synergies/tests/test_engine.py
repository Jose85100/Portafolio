"""Regression tests for the executive operating model."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from ma_valuation import AcquisitionScenario,value_transaction
class Tests(unittest.TestCase):
 def test_incremental_npv(self):
  x=value_transaction(100,110,.1,[AcquisitionScenario("base",1,(22,),(0,))])
  self.assertAlmostEqual(x["expected_deal_npv"],10)
 def test_value_destruction(self):
  x=value_transaction(100,150,.1,[AcquisitionScenario("bad",1,(0,),(0,))])
  self.assertEqual(x["probability_of_value_destruction"],1)

if __name__=="__main__":
 unittest.main()
