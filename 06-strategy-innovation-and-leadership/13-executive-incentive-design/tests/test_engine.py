"""Regression tests for the executive operating model."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from incentives import ExecutiveScore,calculate
class Tests(unittest.TestCase):
 def test_bonus_deferral(self):
  x=calculate([ExecutiveScore("CEO",100,1,1,1,0)])
  self.assertAlmostEqual(x["total_bonus"],100)
  self.assertAlmostEqual(x["total_deferred"],40)
 def test_compliance_override(self):
  x=calculate([ExecutiveScore("CEO",100,1,2,2,0,True)])
  self.assertEqual(x["total_bonus"],0)

if __name__=="__main__":
 unittest.main()
