"""Executive model checks: business invariants and edge cases."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from recovery import RecoveryAction,plan
class Tests(unittest.TestCase):
 def test_recovery(self):
  base=plan(10,2,8,3,[])
  self.assertEqual(base["first_breach_month"],2)
  protected=plan(10,2,8,3,[RecoveryAction("cuts",0,5,1)])
  self.assertIsNone(protected["first_breach_month"])
 def test_action_cost(self):
  x=plan(10,0,0,1,[RecoveryAction("plan",3,0,1)])
  self.assertEqual(x["ending_cash"],7)

if __name__=="__main__":
 unittest.main()
