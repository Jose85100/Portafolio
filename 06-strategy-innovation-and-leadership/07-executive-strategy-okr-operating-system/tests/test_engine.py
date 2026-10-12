"""Executive model checks: business invariants and edge cases."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from okr import KeyResult,evaluate
class Tests(unittest.TestCase):
 def test_progress(self):
  x=evaluate([KeyResult("Revenue","CEO",100,200,150,2),
              KeyResult("Cost","CFO",100,80,80,1,"decrease")])
  self.assertAlmostEqual(x["overall_progress"],2/3)
  self.assertEqual(x["attention_count"],1)
 def test_bad_target(self):
  with self.assertRaises(ValueError): evaluate([KeyResult("A","CEO",1,1,1,1)])

if __name__=="__main__":
 unittest.main()
