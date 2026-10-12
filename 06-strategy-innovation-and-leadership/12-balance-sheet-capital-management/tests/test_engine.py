"""Regression tests for the executive operating model."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from capital_management import BusinessLine,optimize
class Tests(unittest.TestCase):
 def test_capital_constraint(self):
  x=optimize(12,.12,[BusinessLine("A",10,3,10),BusinessLine("B",50,1,2)])
  self.assertEqual(x["allocation"].get("A"),10)
  self.assertAlmostEqual(x["rwa"],100)
 def test_bad_capital(self):
  with self.assertRaises(ValueError): optimize(10,0,[BusinessLine("A",1,1,1)])

if __name__=="__main__":
 unittest.main()
