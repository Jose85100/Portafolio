import math
import random
import unittest
from src.dynamic import DynamicMoments
from src.reduction import merge_balanced


def summarize(xs):
    s = DynamicMoments()
    for x in xs:
        s = s.push(x)
    return s


class ReductionTests(unittest.TestCase):
    def test_identity_and_singleton(self):
        self.assertEqual(merge_balanced([]), DynamicMoments())
        x = summarize([1.0, 2.0])
        self.assertEqual(merge_balanced([x]), x)

    def test_disjoint_partition_oracle(self):
        rng = random.Random(1104)
        for exponent in (-1000, -20, 0, 500, 1000):
            xs = [math.ldexp(rng.uniform(-1, 1), exponent) for _ in range(257)]
            chunks = [summarize(xs[i : i + 7]) for i in range(0, len(xs), 7)]
            got = merge_balanced(chunks)
            # Decimal oracle consumes the same representable binary64 inputs.
            from decimal import Decimal, localcontext

            with localcontext() as ctx:
                ctx.prec = 100
                vals = [Decimal.from_float(x) for x in xs]
                mean = sum(vals) / len(vals)
                var = sum((x - mean) ** 2 for x in vals) / len(vals)
                oracle = float(var.sqrt())
            self.assertLessEqual(
                abs(got.result().std - oracle),
                max(4 * math.ulp(oracle), 1e-12 * oracle),
            )

    def test_reproducible_given_same_order(self):
        xs = [1e12 + math.sin(i) for i in range(1000)]
        chunks = [summarize(xs[i : i + 11]) for i in range(0, len(xs), 11)]
        first = merge_balanced(chunks)
        self.assertEqual(first, merge_balanced(chunks))
        reverse = merge_balanced(chunks[::-1])
        self.assertTrue(math.isfinite(reverse.result().std))
        self.assertLessEqual(abs(first.result().std - reverse.result().std), 1e-10)


if __name__ == "__main__":
    unittest.main()
