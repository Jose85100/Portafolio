"""Regression and invariant checks for the decision engine."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from capital_allocation import InvestmentCase,solve
class EngineTests(unittest.TestCase):
 def test_immediate_exercise(self):
  x=solve(InvestmentCase(120,100,1.2,.8,.5,0,0))
  self.assertEqual(x["option_value"],20)
  self.assertEqual(x["action"],"invest")
 def test_wait_option_nonnegative(self):
  x=solve(InvestmentCase(100,100,1.5,.5,.5,.05,2))
  self.assertGreater(x["option_value"],0)
 def test_bad_probability(self):
  with self.assertRaises(ValueError): solve(InvestmentCase(100,100,1.2,.8,1.5,.05,2))

if __name__=="__main__":
 unittest.main()
