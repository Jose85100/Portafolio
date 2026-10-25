import itertools
import random
import unittest

from src.conformance import arbitrary_verdict, audit, distance


class AuditTests(unittest.TestCase):
    def test_exact_trace(self):
        r = audit([["A"], ["B"], ["C"]], ["A", "B", "C"])
        self.assertEqual((r.lower, r.upper, r.verdict), (0, 0, "conformant"))

    def test_tie_is_not_certain(self):
        r = audit([["A"], ["C", "B"], ["D"]], ["A", "B", "C", "D"])
        self.assertEqual(
            (r.lower, r.upper, r.realizations, r.verdict), (0, 2, 2, "ambiguous")
        )
        self.assertEqual(
            arbitrary_verdict([["A"], ["C", "B"], ["D"]], ["A", "B", "C", "D"]),
            "nonconformant",
        )

    def test_missing_event_definite(self):
        r = audit([["A"], ["C"]], ["A", "B", "C"])
        self.assertEqual((r.lower, r.upper, r.verdict), (1, 1, "nonconformant"))

    def test_empty_trace(self):
        r = audit([], ["A"])
        self.assertEqual((r.lower, r.upper, r.verdict), (1, 1, "nonconformant"))

    def test_budget_refuses_no_fake_bounds(self):
        r = audit([list("ABCDEFG")], list("ABCDEFG"))
        self.assertEqual(
            (r.lower, r.upper, r.realizations, r.verdict),
            (None, None, 0, "budget_exceeded"),
        )

        full = audit([list("ABCDEF"), list("GHI")], list("ABCDEFGHI"))
        self.assertEqual(full.candidate_upper_bound, 4320)

    def test_repeated_labels_unique_orders(self):
        r = audit([["A", "A"]], ["A", "A"])
        self.assertEqual(
            (r.realizations, r.lower, r.upper, r.verdict), (1, 0, 0, "conformant")
        )

    def test_permutation_invariance(self):
        for order in itertools.permutations("BCD"):
            r = audit([["A"], order, ["E"]], list("ABCDE"))
            self.assertEqual((r.lower, r.upper, r.verdict), (0, 4, "ambiguous"))

    def test_bounds_cover_every_realization_property(self):
        rng = random.Random(42)
        for _ in range(100):
            labels = list("ABCD")
            rng.shuffle(labels)
            groups = [labels[:2], labels[2:]]
            reference = list("ABCD")
            r = audit(groups, reference)
            values = [
                distance(a + b, reference)
                for a in itertools.permutations(groups[0])
                for b in itertools.permutations(groups[1])
            ]
            self.assertEqual((r.lower, r.upper), (min(values), max(values)))

    def test_distance_properties(self):
        rng = random.Random(18)
        for _ in range(100):
            a = [rng.choice("ABC") for _ in range(rng.randrange(8))]
            b = [rng.choice("ABC") for _ in range(rng.randrange(8))]
            self.assertEqual(distance(a, b), distance(b, a))
            self.assertLessEqual(abs(len(a) - len(b)), distance(a, b))
            self.assertEqual(distance(a, a), 0)

    def test_invalid_inputs(self):
        for buckets, reference in [
            ([[]], ["A"]),
            ([[""]], ["A"]),
            ([["A"]], []),
            ([[1]], ["A"]),
            ([["A"]], list("A" * 33)),
        ]:
            with self.assertRaises(ValueError):
                audit(buckets, reference)
        with self.assertRaises(ValueError):
            audit(["AB"], ["A", "B"])
        for budget in [0, -1, True, 1.5]:
            with self.assertRaises(ValueError):
                audit([["A"]], ["A"], budget)


if __name__ == "__main__":
    unittest.main()
