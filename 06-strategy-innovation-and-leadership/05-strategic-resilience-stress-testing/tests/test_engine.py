"""Regression and invariant checks for the decision engine."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from resilience import Scenario,evaluate
class EngineTests(unittest.TestCase):
 def test_stress_probability(self):
  s=[Scenario("base",.7,1,1),Scenario("stress",.3,.1,1)]
  x=evaluate(10,10,8,3,s)
  self.assertAlmostEqual(x["breach_probability"],.3)
  self.assertEqual(x["scenarios"][0]["first_breach_month"],None)
  self.assertEqual(x["scenarios"][1]["first_breach_month"],2)
 def test_delay(self):
  x=evaluate(5,10,6,2,[Scenario("late",1,1,1,1)])
  self.assertEqual(x["scenarios"][0]["first_breach_month"],1)

if __name__=="__main__":
 unittest.main()
