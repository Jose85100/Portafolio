import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import unittest
from evsi import Price,choose,evaluate,predictive_prob
class Tests(unittest.TestCase):
 def setUp(self): self.ps=[Price('a',100,11,9),Price('b',180,5,15)]
 def test_predictive_mass(self): self.assertAlmostEqual(sum(predictive_prob(x,20,11,9) for x in range(21)),1,12)
 def test_evsi_nonnegative(self): self.assertGreaterEqual(evaluate(self.ps,20,0)['evsi'],-1e-10)
 def test_more_info_not_lower(self): self.assertGreaterEqual(evaluate(self.ps,20,0)['expected_value_after_sample'],choose(self.ps).value)
 def test_cost_gate(self): self.assertEqual(evaluate(self.ps,20,1e9)['decision'],'launch_now_or_close')
 def test_cost_monotonic(self):
  low=evaluate(self.ps,20,0)['decision']
  high=evaluate(self.ps,20,1e9)['decision']
  self.assertEqual(low,'pilot'); self.assertEqual(high,'launch_now_or_close')
 def test_reject_invalid(self):
  with self.assertRaises(ValueError): predictive_prob(5,4,8,12)
  with self.assertRaises(ValueError): evaluate(self.ps,-1,0)
if __name__=='__main__': unittest.main()
