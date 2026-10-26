import random
import unittest

from src.evaluation import Design, evaluate, interval_decision


class EvaluationTests(unittest.TestCase):
    def test_structural_nonidentification(self):
        d = Design((1.0,), ((1.0, 0.0),), ((0.0, 1.0),))
        r = evaluate(d, [(0, 0, 0.3)] * 1000)
        self.assertEqual(
            (r.lower, r.upper, r.unsupported_mass, r.unseen_supported_mass),
            (0.0, 1.0, 1.0, 0.0),
        )
        self.assertEqual(r.midpoint, 0.5)

    def test_missing_sample_not_structural(self):
        d = Design((1.0,), ((0.5, 0.5),), ((0.0, 1.0),))
        r = evaluate(d, [(0, 0, 1.0)] * 10)
        self.assertEqual((r.unsupported_mass, r.unseen_supported_mass), (0.0, 1.0))
        self.assertEqual((r.lower, r.upper), (0.0, 1.0))

    def test_target_supported_despite_logging_zero(self):
        d = Design((1.0,), ((1.0, 0.0),), ((1.0, 0.0),))
        r = evaluate(d, [(0, 0, 0.3)] * 2000)
        self.assertEqual(r.unsupported_mass, 0.0)
        self.assertLess(r.lower, 0.3)
        self.assertGreater(r.upper, 0.3)

    def test_width_floor_property(self):
        rng = random.Random(4)
        for _ in range(100):
            pi = rng.random()
            d = Design((1.0,), ((1.0, 0.0),), ((1 - pi, pi),))
            r = evaluate(d, [(0, 0, rng.random()) for _ in range(20)])
            self.assertGreaterEqual(r.upper - r.lower + 1e-12, pi)
            self.assertTrue(0 <= r.lower <= r.upper <= 1 + 1e-12)

    def test_more_constant_observations_narrows_radius(self):
        d = Design((1.0,), ((1.0,),), ((1.0,),))
        a = evaluate(d, [(0, 0, 0.5)] * 10)
        b = evaluate(d, [(0, 0, 0.5)] * 1000)
        self.assertLess(b.upper - b.lower, a.upper - a.lower)

    def test_empty_log_is_uninformative(self):
        r = evaluate(Design((1.0,), ((0.5, 0.5),), ((0.5, 0.5),)), [])
        self.assertEqual((r.lower, r.upper, r.unseen_supported_mass), (0.0, 1.0, 1.0))
        self.assertIsNone(r.snips_supported)

    def test_known_weighted_mean(self):
        d = Design((1.0,), ((0.5, 0.5),), ((0.25, 0.75),))
        r = evaluate(d, [(0, 0, 0.0), (0, 1, 1.0)])
        self.assertEqual(r.observed_contribution, 0.75)
        self.assertEqual(r.midpoint, 0.75)
        self.assertEqual(r.ips_truncated, 0.75)
        self.assertEqual(r.snips_supported, 0.75)

    def test_impossible_log_rejected(self):
        d = Design((1.0,), ((1.0, 0.0),), ((0.5, 0.5),))
        with self.assertRaises(ValueError):
            evaluate(d, [(0, 1, 0.5)])

    def test_invalid_inputs(self):
        bad = [
            Design((0.9,), ((1.0,),), ((1.0,),)),
            Design((1.0,), ((1.0, 0.0),), ((1.0,),)),
            Design((1.0,), ((float("nan"),),), ((1.0,),)),
        ]
        for d in bad:
            with self.assertRaises(ValueError):
                evaluate(d, [])
        d = Design((1.0,), ((1.0,),), ((1.0,),))
        for row in [(0, 0, 1.1), (True, 0, 0.5), (0, 0, float("nan")), (1, 0, 0.5)]:
            with self.assertRaises(ValueError):
                evaluate(d, [row])
        with self.assertRaises(ValueError):
            evaluate(d, [], 0)

    def test_observationally_identical_worlds(self):
        from src.experiment import generate

        design = Design(
            (0.4, 0.2, 0.4),
            ((0.5, 0.5), (0.5, 0.5), (1.0, 0.0)),
            ((0.5, 0.5), (0.5, 0.5), (0.0, 1.0)),
        )
        low = generate(200, 17, design, 0.0)
        high = generate(200, 17, design, 1.0)
        self.assertEqual(low, high)
        self.assertEqual(evaluate(design, low), evaluate(design, high))

    def test_decision_boundaries(self):
        self.assertEqual(interval_decision(0.6, 0.7), "accept")
        self.assertEqual(interval_decision(0.2, 0.4), "reject")
        self.assertEqual(interval_decision(0.4, 0.6), "abstain")
        self.assertEqual(interval_decision(0.5, 0.5), "abstain")
        with self.assertRaises(ValueError):
            interval_decision(0.7, 0.2)


if __name__ == "__main__":
    unittest.main()
