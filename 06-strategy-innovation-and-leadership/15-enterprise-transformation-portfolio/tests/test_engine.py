"""Regression tests for the executive operating model."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from transformation import Program,select
class Tests(unittest.TestCase):
 def test_precedence_and_capacity(self):
  p=[Program("data",3,2,7),Program("ai",4,2,15,("data",)),Program("marketing",4,4,9)]
  x=select(p,7,4)
  self.assertEqual(x["selected"],("ai","data"))
  self.assertEqual(x["net_value"],15)
 def test_invalid_dependency(self):
  with self.assertRaises(ValueError): select([Program("A",1,1,2,("missing",))],5,5)

if __name__=="__main__":
 unittest.main()
