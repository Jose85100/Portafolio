"""Round-trip, payoff equivalence, negative controls and randomized invariants."""
from pathlib import Path
import sys
import unittest
import numpy as np
from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from strategic import Game, matrices, nfg, parse_nfg, project, lift, strategic_regret
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'mixed-equilibrium-audit/src'))
from mixed import outcomes, mixed_regret


class StrategicTests(unittest.TestCase):
    def test_round_trip(self):
        self.assertEqual(parse_nfg(nfg(Game())), matrices(Game()))

    def test_symmetry(self):
        a, b = matrices(Game(prior=.3))
        self.assertEqual(a, tuple(zip(*b)))

    @settings(max_examples=80, derandomize=True, deadline=None)
    @given(st.lists(st.integers(0, 100), min_size=4, max_size=4))
    def test_equivalence(self, values):
        x = np.array(values, float)/100
        p, r = lift(x[:2]), lift(x[2:])
        np.testing.assert_allclose(np.r_[project(p), project(r)], x, atol=1e-14)
        a, b = matrices(Game())
        self.assertAlmostEqual(float(p @ np.asarray(a, float) @ r+p @ np.asarray(b, float) @ r),
                               outcomes(Game(), x)['lender_payoff'], places=12)
        self.assertLessEqual(strategic_regret(a, b, p, r), mixed_regret(Game(), x)+1e-12)

    def test_many_to_one(self):
        np.testing.assert_equal(project(np.array([.5, 0, 0, .5])), project(np.array([0, .5, .5, 0])))

    def test_bad_simplex(self):
        for bad in ([1, 0], [np.nan, 0, 0, 1], [-1, 1, 0, 1], [0, 0, 0, 0]):
            with self.assertRaises(ValueError):
                project(np.array(bad))

    def test_bad_behavior(self):
        for bad in ([0], [np.inf, 0], [2, 0], [-.1, 1]):
            with self.assertRaises(ValueError):
                lift(np.array(bad))

    def test_bad_nfg(self):
        for bad in (nfg(Game()).replace('Lender 0', 'Unknown'), nfg(Game()).rsplit(' ', 1)[0]):
            with self.assertRaises(ValueError):
                parse_nfg(bad)

    def test_rare_type_negative_control(self):
        g = Game(prior=1e-8, accuracy=1., cost=.5, complementarity=0.)
        a, b = matrices(g)
        p = np.array([1., 0, 0, 0])
        self.assertLess(strategic_regret(a, b, p, p), 1e-8)
        self.assertEqual(mixed_regret(g, np.zeros(4)), .5)

    def test_external_regular_equivalence(self):
        import nashpy
        a, b = matrices(Game())
        eq = list(nashpy.Game(np.asarray(a, float), np.asarray(b, float)).vertex_enumeration())
        self.assertEqual(len(eq), 5)
        for p, r in eq:
            self.assertLess(mixed_regret(Game(), np.clip(np.r_[project(p), project(r)], 0, 1)), 1e-8)


if __name__ == '__main__':
    unittest.main()
