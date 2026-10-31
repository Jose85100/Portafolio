"""Oracle, range, order and scale covariance checks."""

import math
import random
import unittest
from decimal import Decimal, localcontext
from src.dynamic import DynamicMoments, dynamic_moments


def oracle(values: list[float], ddof: int = 0) -> float:
    with localcontext() as ctx:
        ctx.prec = 100
        xs = [Decimal(x) for x in values]
        mean = sum(xs) / len(xs)
        return float((sum((x - mean) ** 2 for x in xs) / (len(xs) - ddof)).sqrt())


class DynamicTests(unittest.TestCase):
    def test_oracle_orders(self):
        rng = random.Random(31)
        for exponent in [-1070, -700, 0, 700, 1020]:
            values = [math.ldexp(rng.uniform(-1, 1), exponent) for _ in range(100)]
            expected = oracle(values)
            for xs in [values, values[::-1], sorted(values)]:
                actual = dynamic_moments(xs).std
                self.assertIsNotNone(actual)
                self.assertLessEqual(
                    abs(actual - expected),
                    max(4 * math.ulp(expected), abs(expected) * 1e-12),
                )

    def test_subnormal(self):
        tiny = math.ulp(0.0)
        self.assertEqual(dynamic_moments([-tiny, tiny]).std, tiny)
        self.assertEqual(dynamic_moments([0.0, tiny]).status, "std_underflow")

    def test_zero_prefix_and_constant(self):
        self.assertAlmostEqual(
            dynamic_moments([0.0, 0.0, 2.0, 4.0]).std, oracle([0.0, 0.0, 2.0, 4.0])
        )
        self.assertEqual(dynamic_moments([1e308] * 10).std, 0.0)
        self.assertEqual(dynamic_moments([0.0] * 10).std, 0.0)

    def test_state_and_rescale(self):
        state = DynamicMoments()
        for value in [1e-300, 2e-300, 1e300]:
            state = state.push(value)
        self.assertGreater(state.rescales, 0)
        self.assertGreater(state.rounded_to_zero, 0)
        self.assertEqual(state.state.n, 3)
        self.assertAlmostEqual(state.result().std / 1e300, math.sqrt(2) / 3)

    def test_range_and_invalid(self):
        self.assertEqual(
            dynamic_moments([-1e308, 1e308], 1).status, "variance_overflow"
        )
        self.assertEqual(
            dynamic_moments([-1.79e308, 1.79e308], 1).status, "std_overflow"
        )
        for xs, ddof in [
            ([], 0),
            ([1.0], 1),
            ([float("nan")], 0),
            ([float("inf")], 0),
            ([1.0, 2.0], 2),
        ]:
            with self.assertRaises(ValueError):
                dynamic_moments(xs, ddof)

    def test_binary_covariance(self):
        xs = [1.0, -2.0, 3.0, 6.0]
        for e in [-600, -10, 10, 600]:
            self.assertAlmostEqual(
                dynamic_moments([math.ldexp(x, e) for x in xs]).std
                / math.ldexp(1.0, e),
                dynamic_moments(xs).std,
            )
