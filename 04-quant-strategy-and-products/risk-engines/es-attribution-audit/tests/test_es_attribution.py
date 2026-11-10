import math
import random
import unittest

from src.es_attribution import attribute_es


class AttributionTests(unittest.TestCase):
    def test_analytic_fractional_boundary(self):
        result = attribute_es([[0.0, 0.0], [10.0, 0.0], [0.0, 20.0]], alpha=0.75)
        self.assertAlmostEqual(result.var, 20.0)
        self.assertAlmostEqual(result.es, 20.0)
        self.assertAlmostEqual(sum(result.contributions), result.es)

    def test_additivity_translation_homogeneity_and_permutation(self):
        rows = [[float(i - 2), float((i * 3) % 7 - 3)] for i in range(20)]
        a = attribute_es(rows, alpha=.8)
        self.assertAlmostEqual(sum(a.contributions), a.es)
        shifted = [[x + 2 for x in row] for row in rows]
        self.assertAlmostEqual(attribute_es(shifted, alpha=.8).es, a.es + 4)
        scaled = [[x * 4 for x in row] for row in rows]
        self.assertAlmostEqual(attribute_es(scaled, alpha=.8).es, 4 * a.es)
        permuted = list(reversed(rows))
        b = attribute_es(permuted, alpha=.8)
        self.assertAlmostEqual(a.es, b.es)

    def test_weighted_replication_oracle(self):
        rng = random.Random(44)
        for _ in range(100):
            vals = [[rng.randint(-5, 20), rng.randint(-4, 9)] for _ in range(8)]
            weights = [rng.randint(1, 4) for _ in vals]
            expanded = [row for row, w in zip(vals, weights) for _ in range(w)]
            alpha = .75
            weighted = attribute_es(vals, alpha=alpha, scenario_weights=weights)
            reference = attribute_es(expanded, alpha=alpha)
            self.assertAlmostEqual(weighted.var, reference.var)
            self.assertAlmostEqual(weighted.es, reference.es, places=10)
            self.assertTrue(all(math.isfinite(x) for x in weighted.contributions))

    def test_rejects_invalid_inputs(self):
        for alpha in (0.0, 1.0, float("nan")):
            with self.assertRaises(ValueError):
                attribute_es([[1.0]], alpha=alpha)
        for rows, weights in (([], None), ([[1.0], [2.0, 3.0]], None), ([[1.0]], [0.0])):
            with self.assertRaises(ValueError):
                attribute_es(rows, alpha=.95, scenario_weights=weights)


if __name__ == "__main__":
    unittest.main()
