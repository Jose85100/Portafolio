"""Unit, edge, generative and negative controls (stdlib unittest)."""
import math
import random
import unittest

from src.ope import Log, METHODS, REWARDS, crossfit_reward, estimate, simulate, target_action, true_value


class OpeTests(unittest.TestCase):
    def test_oracle(self):
        self.assertAlmostEqual(true_value(), 0.625)

    def test_determinism(self):
        self.assertEqual(simulate(21), simulate(21))
        self.assertNotEqual(simulate(21), simulate(22))

    def test_binary_actions(self):
        for x in (0, 1):
            self.assertEqual(target_action(x), 1 - x)
        with self.assertRaises(ValueError):
            target_action(3)

    def test_crossfit_no_self_leakage(self):
        log = simulate(2, n=90)
        p1 = crossfit_reward(log)
        rewards = list(log.rewards)
        rewards[0] = 1 - rewards[0]
        altered = Log(log.contexts, log.actions, tuple(rewards), log.reported_propensities, log.actual_target_probability)
        p2 = crossfit_reward(altered)
        self.assertEqual(p1[0], p2[0])

    def test_estimators_finite(self):
        log = simulate(42)
        for method in METHODS:
            e = estimate(log, method)
            self.assertTrue(math.isfinite(e.value))
            self.assertTrue(e.ess > 0)

    def test_ess_equal_matched_for_constant_propensity(self):
        log = simulate(9, target_probability=0.04)
        e = estimate(log, "ips")
        self.assertAlmostEqual(e.ess, e.matched)

    def test_weak_overlap_gate(self):
        e = estimate(simulate(9, target_probability=0.04), "dr", min_ess=100)
        self.assertEqual(e.warning, "LOW_ESS")

    def test_perfect_outcome_model_dr_unbiased_even_wrong_propensity_in_expectation(self):
        log = simulate(7, n=20000, target_probability=0.1, reported_probability=0.5)
        exact = tuple(REWARDS[x][target_action(x)] for x in log.contexts)
        dr = estimate(log, "dr", predictions=exact)
        self.assertLess(abs(dr.value - true_value()), 0.04)
        self.assertGreater(abs(estimate(log, "ips").value - true_value()), 0.2)

    def test_clipped_ips_negative_bias_in_low_overlap(self):
        log = simulate(5, n=10000, target_probability=0.04)
        ips = estimate(log, "ips").value
        clipped = estimate(log, "clipped_ips").value
        self.assertGreater(ips, clipped)

    def test_invalid_support(self):
        with self.assertRaises(ValueError):
            simulate(1, target_probability=0)
        with self.assertRaises(ValueError):
            simulate(1, reported_probability=0)

    def test_invalid_observations(self):
        log = simulate(1, n=20)
        bad = Log(log.contexts, log.actions, log.rewards, (float("nan"),) + log.reported_propensities[1:], 0.5)
        with self.assertRaises(ValueError):
            bad.validate()

    def test_invalid_folds_and_clip(self):
        log = simulate(1, n=20)
        with self.assertRaises(ValueError):
            crossfit_reward(log, folds=1)
        with self.assertRaises(ValueError):
            estimate(log, "dr", clip=-1)

    def test_no_target_observations_abstention(self):
        log = Log((0, 1, 0, 1), (0, 1, 0, 1), (1, 0, 0, 1), (0.8,) * 4, 0.2)
        e = estimate(log, "snips")
        self.assertTrue(math.isnan(e.value))
        self.assertEqual(e.warning, "NO_OBSERVED_TARGET_ACTION")

    def test_all_invalid_contracts(self):
        log = simulate(1, n=20)
        with self.assertRaises(ValueError):
            Log(log.contexts, log.actions[:-1], log.rewards, log.reported_propensities, 0.5).validate()
        with self.assertRaises(ValueError):
            Log(log.contexts, (7,) + log.actions[1:], log.rewards, log.reported_propensities, 0.5).validate()
        with self.assertRaises(ValueError):
            Log(log.contexts, log.actions, log.rewards, log.reported_propensities, 0.0).validate()
        with self.assertRaises(ValueError):
            simulate(1, n=2)
        with self.assertRaises(ValueError):
            crossfit_reward(log, prior_strength=0)
        with self.assertRaises(ValueError):
            estimate(log, "bogus")
        with self.assertRaises(ValueError):
            estimate(log, "dr", predictions=(0.1,))

    def test_generative_bounds_and_repeatability(self):
        rng = random.Random(20261015)
        for _ in range(100):
            seed = rng.randrange(1_000_000)
            p = rng.uniform(0.02, 0.95)
            log = simulate(seed, n=30, target_probability=p)
            preds = crossfit_reward(log)
            self.assertEqual(preds, crossfit_reward(log))
            self.assertTrue(all(0 <= v <= 1 for v in preds))
            for m in METHODS:
                e = estimate(log, m, predictions=preds)
                self.assertGreaterEqual(e.ess, 0)
                self.assertLessEqual(e.matched, len(log.contexts))


if __name__ == "__main__":
    unittest.main()
