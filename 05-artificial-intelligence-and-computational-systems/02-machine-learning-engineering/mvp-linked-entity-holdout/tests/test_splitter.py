import random
import unittest
from src.splitter import Record, components, split, leaked_components


class Tests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            Record("a", ("x",)),
            Record("b", ("x", "y")),
            Record("c", ("y",)),
            Record("d", ("z",)),
        ]

    def test_transitive(self):
        self.assertEqual(components(self.rows), dict(a="a", b="a", c="a", d="d"))

    def test_no_leak(self):
        for seed in range(100):
            self.assertEqual(
                leaked_components(self.rows, split(self.rows, "component", seed)), 0
            )

    def test_permutation(self):
        expected = split(self.rows, "component")
        rng = random.Random(29)
        for _ in range(100):
            rng.shuffle(self.rows)
            self.assertEqual(split(self.rows, "component"), expected)

    def test_invalid(self):
        for rows in [
            [Record("a", ())],
            [Record("", ("x",))],
            [Record("a", ("",))],
            self.rows + self.rows[:1],
        ]:
            with self.assertRaises(ValueError):
                components(rows)

    def test_one_component(self):
        with self.assertRaises(ValueError):
            split(self.rows[:3], "component")

    def test_empty(self):
        self.assertEqual(components([]), {})
        with self.assertRaises(ValueError):
            split([], "component")

    def test_unknown(self):
        with self.assertRaises(ValueError):
            split(self.rows, "bad")

    def test_assignment_validation(self):
        with self.assertRaises(ValueError):
            leaked_components(self.rows, {})

    def test_duplicate_tokens(self):
        self.assertEqual(
            components([Record("x", ("a", "a")), Record("y", ("a",))]),
            dict(x="x", y="x"),
        )

    def test_cut_detection(self):
        self.assertEqual(
            leaked_components(
                self.rows, dict(a="train", b="train", c="test", d="test")
            ),
            1,
        )


if __name__ == "__main__":
    unittest.main()
