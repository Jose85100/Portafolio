import itertools
import random
import unittest
from src.balancing import balanced_split, count_split, fixture
from src.splitter import leaked_components, split


class BalanceTests(unittest.TestCase):
    def test_bruteforce_optimum(self):
        rng = random.Random(30)
        for _ in range(100):
            sizes = [rng.randint(1, 9) for _ in range(rng.randint(2, 7))]
            p, q = rng.choice([(1, 4), (1, 3), (1, 2), (2, 3), (3, 4)])
            records = fixture(sizes)
            answer = balanced_split(records, p, q)
            mass = sum(v == "train" for v in answer.values())
            oracle = min(
                abs(q * sum(s * b for s, b in zip(sizes, bits)) - p * sum(sizes))
                for bits in itertools.product([0, 1], repeat=len(sizes))
                if 0 < sum(bits) < len(sizes)
            )
            self.assertEqual(abs(q * mass - p * sum(sizes)), oracle)
            self.assertEqual(leaked_components(records, answer), 0)

    def test_prior_baseline_unchanged(self):
        rows = fixture([1, 2, 7, 8])
        self.assertEqual(count_split(rows), split(rows, "component"))

    def test_permutation(self):
        rows = fixture([1, 2, 7, 8])
        expected = balanced_split(rows)
        rng = random.Random(30)
        for _ in range(50):
            rng.shuffle(rows)
            self.assertEqual(balanced_split(rows), expected)

    def test_giant_negative(self):
        assignment = balanced_split(fixture([1, 1, 1, 30]))
        self.assertEqual(sum(v == "train" for v in assignment.values()), 3)

    def test_ratio_validation(self):
        for p, q in [(0, 2), (2, 2), (3, 2), (1, 0), (-1, 2), (True, 2), (1, 2.0)]:
            for method in [balanced_split, count_split]:
                with self.assertRaises(ValueError):
                    method(fixture([1, 2]), p, q)

    def test_budget(self):
        with self.assertRaises(ValueError):
            balanced_split(fixture([2, 3]), max_rows=4)

    def test_component_budget(self):
        with self.assertRaises(ValueError):
            balanced_split(fixture([1] * 101))

    def test_degenerate(self):
        for sizes in [[], [9]]:
            with self.assertRaises(ValueError):
                balanced_split(fixture(sizes))

    def test_equivalent_fraction(self):
        self.assertEqual(
            balanced_split(fixture([1, 2, 7, 8]), 1, 2),
            balanced_split(fixture([1, 2, 7, 8]), 2, 4),
        )

    def test_odd_tie_lower_mass(self):
        self.assertEqual(
            sum(v == "train" for v in balanced_split(fixture([1, 2])).values()), 1
        )

    def test_fixture_invalid(self):
        for sizes in [[0], [-1], [1.5]]:
            with self.assertRaises(ValueError):
                fixture(sizes)
