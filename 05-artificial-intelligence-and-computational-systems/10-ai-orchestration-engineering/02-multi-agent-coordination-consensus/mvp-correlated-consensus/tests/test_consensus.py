"""Contracts, deterministic properties, adversarial and negative controls."""
import itertools
import math
import unittest

from src.consensus import (POLICIES, PROVENANCE, Case, decide, evaluate,
                           fit_reliabilities, generate_cases)
from benchmarks.run import bootstrap_mean_ci, svg_chart


class TestConsensus(unittest.TestCase):
    def setUp(self):
        self.weights = (1.2, 1.2, 1.2, 1.4, 1.4)

    def test_seed_reproducible(self):
        self.assertEqual(generate_cases(7, 25, .2), generate_cases(7, 25, .2))
        self.assertNotEqual(generate_cases(7, 25, .2), generate_cases(8, 25, .2))

    def test_invalid_generator(self):
        for n, p in [(0, .2), (1, -0.1), (1, 1.1)]:
            with self.assertRaises(ValueError):
                generate_cases(1, n, p)

    def test_calibration_has_finite_positive_weights(self):
        w = fit_reliabilities(generate_cases(3, 800, .2))
        self.assertEqual(len(w), 5)
        self.assertTrue(all(math.isfinite(x) and x > 0 for x in w))

    def test_calibration_is_laplace_smoothed(self):
        all_correct = [Case(i, 1, (1, 1, 1, 1, 1)) for i in range(20)]
        self.assertTrue(all(math.isfinite(w) for w in fit_reliabilities(all_correct)))

    def test_calibration_rejects_empty_and_invalid(self):
        for cases in ([], [Case(1, 3, (0, 0, 0, 0, 0))], [Case(1, 1, (1, 1))]):
            with self.assertRaises(ValueError):
                fit_reliabilities(cases)

    def test_exhaustive_32_vote_patterns(self):
        for votes in itertools.product((0, 1), repeat=5):
            for policy in POLICIES:
                result = decide(votes, self.weights, policy)
                self.assertIn(result.prediction, (0, 1))
                self.assertTrue(0 <= result.confidence <= 1)

    def test_majority_exact(self):
        for votes in itertools.product((0, 1), repeat=5):
            self.assertEqual(decide(votes, self.weights, "majority").prediction, int(sum(votes) >= 3))

    def test_unanimous_group_cap_is_unit_margin(self):
        for vote in (0, 1):
            result = decide((vote,) * 5, self.weights, "group_capped")
            self.assertEqual(result.prediction, vote)
            self.assertAlmostEqual(result.confidence, 1)

    def test_all_singleton_groups_match_weighted(self):
        votes = (1, 1, 0, 0, 1)
        a = decide(votes, self.weights, "group_capped", ("a", "b", "c", "d", "e"))
        b = decide(votes, self.weights, "weighted")
        # Predictions can differ with non-equal weights because group cap uses unit group votes;
        # with equal weights they are identical.
        ones = (1.,) * 5
        self.assertEqual(decide(votes, ones, "group_capped", ("a", "b", "c", "d", "e")),
                         decide(votes, ones, "weighted"))
        self.assertTrue(0 <= a.confidence <= 1 and 0 <= b.confidence <= 1)

    def test_wrong_metadata_ablation_equivalent_to_weighted(self):
        for votes in itertools.product((0, 1), repeat=5):
            self.assertEqual(decide(votes, self.weights, "wrong_metadata"),
                             decide(votes, self.weights, "weighted"))

    def test_invalid_votes_weights_groups_policy(self):
        bad = [((0, 1), self.weights, "weighted", PROVENANCE),
               ((0, 1, 0, 1, 2), self.weights, "weighted", PROVENANCE),
               ((0, 1, 0, 1, 1), (1, 2), "weighted", PROVENANCE),
               ((0, 1, 0, 1, 1), (1, 2, 0, 1, 1), "weighted", PROVENANCE),
               ((0, 1, 0, 1, 1), (1, 2, float("nan"), 1, 1), "weighted", PROVENANCE),
               ((0, 1, 0, 1, 1), self.weights, "unknown", PROVENANCE),
               ((0, 1, 0, 1, 1), self.weights, "weighted", ("a",))]
        for args in bad:
            with self.subTest(args=args), self.assertRaises(ValueError):
                decide(*args)

    def test_evaluate_exact_80pct_coverage(self):
        test = generate_cases(23, 600, .2)
        w = fit_reliabilities(generate_cases(24, 800, .2))
        for policy in POLICIES:
            metrics = evaluate(test, w, policy)
            self.assertEqual(metrics["coverage"], 0.8)
            for name in ("accuracy", "risk_at_80", "aurc", "mean_margin"):
                self.assertTrue(0 <= metrics[name] <= 1)

    def test_evaluate_rejects_empty_invalid_coverage(self):
        c = generate_cases(1, 5, 0)
        for cases, cov in [((), .8), (c, 0), (c, 1.2)]:
            with self.assertRaises(ValueError):
                evaluate(cases, self.weights, "majority", cov)
        with self.assertRaises(ValueError):
            evaluate(c, self.weights, "bad")

    def test_no_label_leakage_in_prediction(self):
        c = generate_cases(1, 1, .2)[0]
        flipped = Case(c.case_id, 1 - c.truth, c.votes)
        for policy in POLICIES:
            a = evaluate([c], self.weights, policy)
            b = evaluate([flipped], self.weights, policy)
            self.assertEqual(a["mean_margin"], b["mean_margin"])
            self.assertEqual(a["accuracy"] + b["accuracy"], 1)

    def test_bootstrap_reproducible_and_constant(self):
        self.assertEqual(bootstrap_mean_ci([.2] * 10), (.2, .2))
        self.assertEqual(bootstrap_mean_ci([1, 2, 3]), bootstrap_mean_ci([1, 2, 3]))

    def test_svg_has_all_policies(self):
        payload = {"independent": {p: {"risk_at_80": .2} for p in POLICIES}}
        svg = svg_chart(payload)
        self.assertIn("<svg", svg)
        self.assertIn("group capped", svg)


if __name__ == "__main__":
    unittest.main()
