import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from experiment import Row, compare_policies, evaluate, generate, known_mean


class CausalEvaluationTests(unittest.TestCase):
    def test_exact_hand_calculation(self):
        rows = [Row(0.5, 1, 1.0, 0.5), Row(0.5, 0, 0.0, 0.5)]
        result = evaluate(rows, lambda x: 1, lambda x, a: 0.2)
        self.assertAlmostEqual(result["direct"], 0.2)
        self.assertAlmostEqual(result["ips"], 1.0)
        self.assertAlmostEqual(result["aipw"], 1.0)
        self.assertEqual(result["matched"], 1)
        self.assertEqual(result["effective_sample_size"], 1.0)

    def test_paired_policy_difference_and_standard_error(self):
        rows = [Row(0.5, 1, 1.0, 0.5), Row(0.5, 0, 0.0, 0.5)]
        comparison = compare_policies(rows, lambda x: 1, lambda x: 0, lambda x, a: 0)
        self.assertEqual(comparison["aipw_difference"], 1.0)
        self.assertAlmostEqual(comparison["aipw_difference_se"], 1.0)
        self.assertAlmostEqual(comparison["normal_95_low"], 1 - 1.959963984540054)
        same = compare_policies(rows, lambda x: 1, lambda x: 1, known_mean)
        self.assertEqual(same["aipw_difference"], 0)
        self.assertEqual(same["aipw_difference_se"], 0)
        with self.assertRaises(ValueError):
            compare_policies(rows[:1], lambda x: 1, lambda x: 0, known_mean)

    def test_known_value_with_misspecified_outcome_model(self):
        # Known propensities alone correct the deliberately wrong outcome model.
        rows = generate(40000, seed=20)
        r = evaluate(rows, lambda x: int(x >= .125), lambda x, a: 0)
        self.assertLess(abs(r["aipw"] - 0.30625), 4 * r["aipw_se"])
        self.assertEqual(r["direct"], 0)

    def test_generator_is_reproducible(self):
        self.assertEqual(generate(10, 3), generate(10, 3))
        self.assertNotEqual(generate(10, 3), generate(10, 4))

    def test_reject_all_has_zero_value(self):
        r = evaluate(generate(100, 5), lambda x: 0, known_mean)
        self.assertEqual(r["aipw"], 0)
        self.assertEqual(r["aipw_se"], 0)

    def test_invalid_inputs_and_no_overlap(self):
        for p in (0, 1, -0.1, math.nan):
            with self.subTest(p=p), self.assertRaises(ValueError):
                evaluate([Row(0.5, 1, 1, p)] * 2, lambda x: 1, known_mean)
        with self.assertRaises(ValueError):
            evaluate(generate(2), lambda x: 2, known_mean)
        with self.assertRaises(ValueError):
            evaluate(generate(2), lambda x: 1, lambda x, a: math.nan)
        with self.assertRaises(ValueError):
            generate(1)


if __name__ == "__main__":
    unittest.main()
