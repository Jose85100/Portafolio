"""Regression and invariant checks for the decision engine."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from market_entry import pure_nash,mixed_nash,dominance
class EngineTests(unittest.TestCase):
 def test_prisoners_dilemma(self):
  game=[[(-1,-1),(-3,0)],[(0,-3),(-2,-2)]]
  self.assertEqual(pure_nash(game),[(1,1)])
  self.assertEqual(dominance(game),{"row":1,"column":1})
 def test_matching_pennies(self):
  game=[[(1,-1),(-1,1)],[(-1,1),(1,-1)]]
  self.assertEqual(pure_nash(game),[])
  m=mixed_nash(game)
  self.assertAlmostEqual(m["row_action_0_probability"],.5)
  self.assertAlmostEqual(m["column_action_0_probability"],.5)

if __name__=="__main__":
 unittest.main()
