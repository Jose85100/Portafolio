import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

import numpy as np
from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.mixed import (DegenerateGameError, Game, affine, mixed_regret, outcomes,
                       pure_baseline, rational_oracle, solve)


class MixedTests(unittest.TestCase):
    def test_main_five(self):
        points = solve(Game())
        self.assertEqual(len(points), 5)
        self.assertEqual(len(pure_baseline(Game())), 3)
        expected = np.array([0, 25/136, 0, 25/136])
        self.assertTrue(any(np.allclose(p, expected) for p in points))
        self.assertTrue(all(mixed_regret(Game(), p) < 1e-12 for p in points))

    def test_exact_oracle(self):
        a = solve(Game())
        b = np.array(rational_oracle(Game()), dtype=float)
        self.assertEqual(len(a), len(b))
        for p in a:
            self.assertLess(min(np.max(np.abs(p-q)) for q in b), 1e-12)

    def test_pure_contained(self):
        g = Game()
        points = solve(g)
        self.assertTrue(all(any(np.array_equal(p, q) for q in points) for p in pure_baseline(g)))

    def test_no_externality_unique(self):
        self.assertEqual(len(solve(Game(complementarity=0))), 1)

    def test_degenerate_fail_closed(self):
        with self.assertRaises(DegenerateGameError):
            solve(Game(accuracy=.5, cost=.5, complementarity=0))

    def test_lp_failure_not_infeasibility(self):
        with patch('src.mixed.linprog', return_value=SimpleNamespace(status=1, success=False, message='limit')):
            with self.assertRaises(RuntimeError):
                solve(Game(accuracy=.5, cost=.5, complementarity=0))

    def test_outcome_matches_pure(self):
        self.assertAlmostEqual(outcomes(Game(), np.array([0., 1., 0., 1.]))['freeze_given_good'], .04)

    def test_additional_equilibrium_not_new_extrema(self):
        values = [outcomes(Game(), p)['freeze_given_good'] for p in solve(Game())]
        self.assertAlmostEqual(min(values), 0)
        self.assertAlmostEqual(max(values), 1)

    def test_validation(self):
        for x in (np.zeros(3), np.array([0, 0, 0, np.nan]), np.array([0, 0, 0, 1.1])):
            with self.assertRaises(ValueError):
                mixed_regret(Game(), x)
        for tol in (0, -1, np.inf, .1):
            with self.assertRaises(ValueError):
                solve(Game(), tol)

    def test_fully_mixed_infeasible_main(self):
        b, a = affine(Game())
        x = np.linalg.solve(a, -b)
        self.assertTrue(np.any(x < 0) or np.any(x > 1))

    @settings(max_examples=40, derandomize=True, deadline=None)
    @given(st.integers(61, 94), st.integers(11, 149), st.integers(21, 139))
    def test_oracle_property(self, q, c, alpha):
        g = Game(accuracy=q/100, cost=c/100, complementarity=alpha/100)
        try:
            points = solve(g)
        except DegenerateGameError:
            return  # Degeneracy is explicitly outside finite-list scope.
        oracle = np.array(rational_oracle(g), dtype=float)
        self.assertEqual(len(points), len(oracle))
        for p in points:
            self.assertLessEqual(mixed_regret(g, p), 1e-10)
            self.assertLess(min(np.max(np.abs(p-v)) for v in oracle), 1e-9)

    @settings(max_examples=100, derandomize=True)
    @given(st.lists(st.floats(0, 1, allow_nan=False, allow_infinity=False), min_size=4, max_size=4))
    def test_probability_property(self, probabilities):
        result = outcomes(Game(), np.array(probabilities))
        self.assertTrue(0 <= result['lending_rate'] <= 1+1e-12)
        self.assertTrue(0 <= result['freeze_given_good'] <= 1+1e-12)


if __name__ == '__main__':
    unittest.main()
