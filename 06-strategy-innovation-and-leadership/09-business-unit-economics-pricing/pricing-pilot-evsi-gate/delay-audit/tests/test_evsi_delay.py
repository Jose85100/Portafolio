import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from evsi_delay import Arm, analyze, predictive


class TestEVSI(unittest.TestCase):
    def setUp(self):
        self.a=Arm(11,9,10)
        self.b=Arm(9,11,12)
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
    def test_delay_cost_identity_and_threshold(self):
        immediate = analyze(self.a, self.b, 10, 100, 0, 2)
        delayed = analyze(self.a, self.b, 10, 100, 5, 2)
        self.assertAlmostEqual(immediate["pilot_value"]-delayed["pilot_value"],
                               5*immediate["posterior_best_margin"], places=10)
        self.assertGreater(immediate["net_gain"], delayed["net_gain"])
    def test_delay_aware_rule_can_reverse_evsi_rule(self):
        from evsi import Price, evaluate
        legacy = evaluate([Price("A",10,11,9),Price("B",12,9,11)],10,0)
        delayed = analyze(self.a,self.b,10,100,10,0)
        self.assertEqual(legacy["decision"], "pilot")
        self.assertEqual(delayed["decision"], "immediate")
    def test_arm_rejects_invalid_parameters(self):
        with self.assertRaises(ValueError): Arm(0,1,1)
        with self.assertRaises(ValueError): Arm(1,1,-1)
    def test_exact_evsi_nonnegative_with_rounding_flag(self):
        r=analyze(self.a,self.b,10,100,0,0)
        self.assertGreaterEqual(r["evsi"],-1e-8)
        self.assertAlmostEqual(r["predictive_mass"],1,places=12)
    def test_high_concentration_roundoff_is_exposed_not_clipped(self):
        a,b=Arm(11000,9000,10),Arm(9000,11000,12)
        r=analyze(a,b,10,100,0,0)
        self.assertLess(r["evsi"],0)
        self.assertTrue(r["evsi_negative_roundoff"])
        self.assertNotEqual(r["predictive_mass"],1.0)
    def test_integer_design_inputs_required(self):
        with self.assertRaises(ValueError): analyze(self.a,self.b,1.5,100,0,0)
if __name__=="__main__":
    unittest.main()
