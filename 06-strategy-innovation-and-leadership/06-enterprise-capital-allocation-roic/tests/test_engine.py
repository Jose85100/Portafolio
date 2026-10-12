"""Executive model checks: business invariants and edge cases."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from capital import BusinessUnit,allocate
class Tests(unittest.TestCase):
 def test_eva_and_budget(self):
  x=allocate([BusinessUnit("A",10,4,.1),BusinessUnit("B",8,.5,.1)],10)
  self.assertEqual(x["selected"],("A",))
  self.assertAlmostEqual(x["expected_eva"],3)
 def test_invalid_wacc(self):
  with self.assertRaises(ValueError): allocate([BusinessUnit("A",1,2,1.1)],1)

if __name__=="__main__":
 unittest.main()
