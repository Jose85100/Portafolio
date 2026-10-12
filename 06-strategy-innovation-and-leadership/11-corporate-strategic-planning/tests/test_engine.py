"""Regression tests for the executive operating model."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from strategic_plan import Scenario,forecast
class Tests(unittest.TestCase):
 def test_deterministic_cash(self):
  x=forecast(100,10,.3,[Scenario("base",1,(.1,),(.2,),(.05,),.1)])
  self.assertAlmostEqual(x["expected_terminal_cash"],10+22-6.6-5.5-1)
 def test_bad_probability(self):
  with self.assertRaises(ValueError): forecast(100,0,.3,[Scenario("bad",.5,(0,),(.2,),(.1,),.1)])

if __name__=="__main__":
 unittest.main()
