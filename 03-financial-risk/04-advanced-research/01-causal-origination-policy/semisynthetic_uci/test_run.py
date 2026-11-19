import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run


class SemisyntheticTests(unittest.TestCase):
    def test_known_truth_and_determinism(self):
        xs = [0.0, 0.25, 0.5, 1.0]
        result = run.run(xs)
        self.assertEqual(result, run.run(xs))
        self.assertAlmostEqual(result['always']['conditional_truth'], 0.25)
        self.assertAlmostEqual(result['never']['aipw'], 0)
        self.assertEqual(result['threshold_0.125']['n'], 4)

    def test_bad_covariate(self):
        for x in [-0.1, 1.1, float('nan')]:
            with self.assertRaises(ValueError):
                run.simulate([x])

    def test_source_hash_validation(self):
        with self.assertRaises(ValueError):
            run.load_x(Path(__file__))


if __name__ == '__main__':
    unittest.main()
