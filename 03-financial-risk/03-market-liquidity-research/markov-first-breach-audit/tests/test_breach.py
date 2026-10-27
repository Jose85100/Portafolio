import itertools
import math
import unittest

from src.breach import first_breach, minimum_buffer


class TestBreach(unittest.TestCase):
    def test_exhaustive_path_oracle(self):
        P = [[0.95, 0.05], [0.2, 0.8]]
        pi = [0.8, 0.2]
        increments = [1, -2]
        for horizon in range(1, 7):
            expected = [0.0] * horizon
            terminal = 0.0
            for path in itertools.product(range(2), repeat=horizon):
                probability = pi[path[0]] * math.prod(
                    P[a][b] for a, b in itertools.pairwise(path)
                )
                cash = 2
                hit = None
                for day, state in enumerate(path):
                    cash += increments[state]
                    if cash < 0 and hit is None:
                        hit = day
                if hit is not None:
                    expected[hit] += probability
                if cash < 0:
                    terminal += probability
            result = first_breach(2, horizon, increments, P, pi)
            for a, b in zip(result.first_breach, expected):
                self.assertAlmostEqual(a, b, places=13)
            self.assertAlmostEqual(result.terminal_negative, terminal, places=13)

    def test_recovery_is_not_survival(self):
        # Deterministic -2 then+3: terminal positive, but day1 breaches from1.
        result = first_breach(1, 2, [-2, 3], [[0, 1], [0, 1]], [1, 0])
        self.assertEqual(result.breach_probability, 1)
        self.assertEqual(result.terminal_negative, 0)
        self.assertEqual(result.first_breach, (1.0, 0.0))

    def test_zero_boundary_and_empty_horizon(self):
        self.assertEqual(first_breach(2, 1, [-2], [[1]], [1]).breach_probability, 0)
        self.assertEqual(first_breach(2, 2, [-2], [[1]], [1]).first_breach, (0.0, 1.0))
        self.assertEqual(first_breach(0, 0, [1], [[1]], [1]).survival, 1)

    def test_monotonicity_mass_and_buffer(self):
        P = [[0.8, 0.2], [0.8, 0.2]]
        pi = [0.8, 0.2]
        inc = [1, -2]
        results = [first_breach(b, 10, inc, P, pi) for b in range(11)]
        risks = [r.breach_probability for r in results]
        self.assertEqual(risks, sorted(risks, reverse=True))
        for r in results:
            self.assertAlmostEqual(r.breach_probability + r.survival, 1, places=12)
            self.assertLessEqual(r.terminal_negative, r.breach_probability + 1e-12)
            self.assertLess(r.maximum_mass_error, 1e-12)
        buffer = minimum_buffer(10, inc, P, pi, 0.05, 20)
        self.assertIsNotNone(buffer)
        self.assertLessEqual(
            first_breach(buffer, 10, inc, P, pi).breach_probability, 0.05
        )
        self.assertIsNone(minimum_buffer(10, inc, P, pi, 0, 0))

    def test_stationary_marginals_and_one_day_ablation(self):
        pi = [0.8, 0.2]
        models = [[[0.8, 0.2], [0.8, 0.2]], [[0.95, 0.05], [0.2, 0.8]]]
        for P in models:
            next_pi = [sum(pi[i] * P[i][j] for i in range(2)) for j in range(2)]
            for a, b in zip(next_pi, pi):
                self.assertAlmostEqual(a, b, places=14)
        a = first_breach(1, 1, [1, -2], models[0], pi)
        b = first_breach(1, 1, [1, -2], models[1], pi)
        self.assertEqual(a.breach_probability, b.breach_probability)

    def test_invalid(self):
        for args in [
            (-1, 2, [1], [[1]], [1]),
            (True, 2, [1], [[1]], [1]),
            (1, 201, [1], [[1]], [1]),
            (1, True, [1], [[1]], [1]),
            (1, 2, [], [], []),
            (1, 2, [0.1], [[1]], [1]),
            (1, 200, [1000], [[1]], [1]),
            (1, 2, [1], [[0.9]], [1]),
            (1, 2, [1], [[1]], [math.nan]),
            (1, 2, [1], [[1, 0]], [1]),
        ]:
            with self.assertRaises(ValueError):
                first_breach(*args)
        for target, maximum in [(math.nan, 10), (-1, 10), (0.05, -1), (0.05, True)]:
            with self.assertRaises(ValueError):
                minimum_buffer(1, [1], [[1]], [1], target, maximum)
