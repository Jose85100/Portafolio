"""Regression and invariant checks for the decision engine."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from investment_prioritization import Initiative,optimize
class EngineTests(unittest.TestCase):
 def test_budget_and_dependency(self):
  items=[Initiative("foundation",3,(5,5)),Initiative("model",4,(12,12),("foundation",)),Initiative("dashboard",4,(8,8))]
  x=optimize(items,7,(.5,.5))
  self.assertEqual(x["selected"],("foundation","model"))
  self.assertEqual(x["total_cost"],7)
 def test_bad_probability(self):
  with self.assertRaises(ValueError): optimize([Initiative("A",1,(2,))],1,(.9,))

if __name__=="__main__":
 unittest.main()
