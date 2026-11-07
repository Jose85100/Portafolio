import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from evsi_delay import Arm,analyze,predictive

class TestEVSI(unittest.TestCase):
    def setUp(self):
        self.a=Arm(11,9,10,20)
        self.b=Arm(9,11,12,24)
    def test_mass(self):
        self.assertAlmostEqual(sum(predictive(k,10,11,9) for k in range(11)),1,places=12)
    def test_zero_information(self):
        self.assertAlmostEqual(analyze(self.a,self.b,0,100,0,0)["net_gain"],0,places=10)
    def test_delay_monotonic(self):
        self.assertLess(analyze(self.a,self.b,10,100,5,0)["pilot_value"],analyze(self.a,self.b,10,100,0,0)["pilot_value"])
    def test_full_delay(self):
        self.assertEqual(analyze(self.a,self.b,10,100,100,0)["pilot_value"],0)
    def test_invalid(self):
        with self.assertRaises(ValueError):
            analyze(self.a,self.b,10,100,101,0)
if __name__=="__main__":
    unittest.main()
