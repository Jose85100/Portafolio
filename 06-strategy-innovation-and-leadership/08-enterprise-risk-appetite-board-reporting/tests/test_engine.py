"""Executive model checks: business invariants and edge cases."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from risk_appetite import RiskMetric,assess
class Tests(unittest.TestCase):
 def test_limits(self):
  x=assess([RiskMetric("NPL",.12,.1),RiskMetric("LCR",1.2,1, direction="lower")])
  self.assertEqual(x["breaches"],1)
  self.assertEqual(x["metrics"][0]["escalation"],"board")
 def test_zero_lower(self):
  x=assess([RiskMetric("LCR",0,1,direction="lower")])
  self.assertEqual(x["breaches"],1)

if __name__=="__main__":
 unittest.main()
