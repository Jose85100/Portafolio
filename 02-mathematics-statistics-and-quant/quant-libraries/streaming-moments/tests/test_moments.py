import unittest
import random
import math
from src.moments import Moments, summarize


class Tests(unittest.TestCase):
    def test_edges(self):
        for ddof in [0, 1, 2]:
            with self.assertRaises(ValueError):
                Moments().variance(ddof)
        self.assertEqual(summarize([2.0]).variance(), 0.0)
        for x in [math.nan, math.inf, -math.inf]:
            with self.assertRaises(ValueError):
                summarize([x])
        self.assertEqual(summarize([7.0] * 40).variance(), 0.0)

    def test_merge_identity(self):
        a = summarize([1.0, 3.0, 5.0])
        self.assertEqual(a.merge(Moments()), a)
        self.assertEqual(Moments().merge(a), a)
        self.assertEqual(a.variance(1), 4.0)

    def test_partitions_and_translation(self):
        rng = random.Random(20261029)
        for _ in range(100):
            x = [float(rng.randrange(-16, 17)) for _ in range(80)]
            ref = sum((z - sum(x) / len(x)) ** 2 for z in x) / len(x)
            for shift in [0.0, 1e12]:
                y = [z + shift for z in x]
                for cut in [1, 17, 79]:
                    out = summarize(y[:cut]).merge(summarize(y[cut:]))
                    self.assertAlmostEqual(out.variance(), ref, places=10)
                self.assertAlmostEqual(summarize(y).variance(), ref, places=10)

    def test_units_and_order(self):
        x = [1.0, 2.0, 4.0, 8.0, 16.0] * 20
        a = summarize(x).variance()
        self.assertAlmostEqual(summarize(reversed(x)).variance(), a, places=11)
        self.assertAlmostEqual(
            summarize([3 * z for z in x]).variance(), 9 * a, places=10
        )
