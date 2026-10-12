import unittest
from model import DeterministicEL, Exposure, example


class TestEL(unittest.TestCase):
    def test_example(self):
        self.assertAlmostEqual(DeterministicEL().calculate(example()), 83)

    def test_empty(self):
        self.assertEqual(DeterministicEL().calculate([]), 0)

    def test_invalid(self):
        for values in [(-0.1, 0.5, 100), (0.1, 1.2, 100),
                       (0.1, 0.5, -1), (float("nan"), 0.5, 100)]:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    Exposure(*values)


if __name__ == "__main__":
    unittest.main()
