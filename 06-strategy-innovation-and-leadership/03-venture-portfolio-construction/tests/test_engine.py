"""Regression and invariant checks for the decision engine."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from venture_portfolio import Startup,simulate
class EngineTests(unittest.TestCase):
 def test_certain_failure(self):
  x=simulate([Startup("A",100,1,0,.2)],scenarios=100,seed=1)
  self.assertEqual(x["expected_profit"],-100)
  self.assertEqual(x["loss_probability"],1)
  self.assertEqual(x["expected_shortfall_loss"],100)
 def test_reproducibility(self):
  inputs=[Startup("A",100,.3,.5,.8),Startup("B",50,.1,.4,.3)]
  self.assertEqual(simulate(inputs,100,seed=8),simulate(inputs,100,seed=8))
 def test_negative_correlation_rejected(self):
  with self.assertRaises(ValueError): simulate([Startup("A",1,0,0,1)],correlation=-.2)

if __name__=="__main__":
 unittest.main()
