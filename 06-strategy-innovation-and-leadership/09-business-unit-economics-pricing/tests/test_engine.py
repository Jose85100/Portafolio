"""Executive model checks: business invariants and edge cases."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from unit_economics import Segment,analyze
class Tests(unittest.TestCase):
 def test_margin_and_ltv(self):
  x=analyze([Segment("SMB",100,20,8,30,500,.1)])["segments"][0]
  self.assertEqual(x["operating_profit"],700)
  self.assertEqual(x["break_even_customers"],42)
  self.assertAlmostEqual(x["ltv_to_cac"],4)
 def test_zero_churn(self):
  x=analyze([Segment("A",1,10,2,1,0,0)])["segments"][0]
  self.assertIsNone(x["ltv_before_cac"])

if __name__=="__main__":
 unittest.main()
