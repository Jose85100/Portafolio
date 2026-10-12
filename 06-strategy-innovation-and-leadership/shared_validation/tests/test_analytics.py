"""Tests for independent statistical validation utilities."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analytics import one_way_sensitivity,bootstrap_mean_interval,weighted_scenario_summary

class ValidationTests(unittest.TestCase):
    def test_sensitivity_keeps_original_parameters_unchanged(self):
        params={"x":2,"y":3}
        result=one_way_sensitivity(lambda p:p["x"]*p["y"],params,"x",[1,4])
        self.assertEqual(params,{"x":2,"y":3})
        self.assertEqual(result["baseline"],6)
        self.assertEqual([x.delta_from_base for x in result["points"]],[-3,6])

    def test_sensitivity_rejects_unknown_input(self):
        with self.assertRaises(ValueError):
            one_way_sensitivity(lambda p:0,{"x":1},"missing",[2])

    def test_bootstrap_constant_sample(self):
        result=bootstrap_mean_interval([7.0]*10,resamples=100,seed=17)
        self.assertEqual((result["lower"],result["upper"]),(7,7))

    def test_bootstrap_reproducible(self):
        x=bootstrap_mean_interval([1,2,3,4],resamples=100,seed=10)
        self.assertEqual(x,bootstrap_mean_interval([1,2,3,4],resamples=100,seed=10))

    def test_weighted_scenarios(self):
        x=weighted_scenario_summary([-10,10],[.25,.75])
        self.assertAlmostEqual(x["expected_value"],5)
        self.assertAlmostEqual(x["downside_probability"],.25)
        self.assertAlmostEqual(x["standard_deviation"],(75)**.5)

    def test_probability_validation(self):
        with self.assertRaises(ValueError):
            weighted_scenario_summary([1,2],[.5,.6])

if __name__=="__main__":
    unittest.main()
