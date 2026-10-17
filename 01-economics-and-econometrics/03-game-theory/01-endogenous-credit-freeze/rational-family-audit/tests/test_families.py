from fractions import Fraction as F
from itertools import product
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from families import Game, matrices, hull, dimension, project, lift, regret, reconstruct, audit, read_game
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'polyhedral-freeze-audit/src'))
from polyhedra import equilibrium_cells, exact_regret


def baseline(g):
    return sorted((c.left.vertices, c.right.vertices) for c in equilibrium_cells(g))


class FamilyTests(unittest.TestCase):
    def test_four_scenarios(self):
        for g in (Game(), Game(accuracy=.5), Game(accuracy=.5, cost=.5, complementarity=0),
                  Game(accuracy=1, cost=1)):
            profiles, cells = audit(g)
            self.assertTrue(profiles)
            self.assertEqual(cells, baseline(g))

    @settings(max_examples=12, derandomize=True, deadline=None)
    @given(st.integers(2, 8), st.integers(5, 10), st.integers(1, 12))
    def test_rational_games(self, pi, q, c):
        g = Game(prior=pi/10, accuracy=q/10, cost=c/10)
        _, cells = audit(g)
        self.assertEqual(cells, baseline(g))
        for left, right in cells:
            for x, y in product(left, right):
                self.assertEqual(exact_regret(g, x+y), 0)

    @settings(max_examples=60, derandomize=True, deadline=None)
    @given(st.lists(st.tuples(st.integers(-5, 5), st.integers(-5, 5)), min_size=1, max_size=12))
    def test_hull_invariants(self, points):
        p = tuple((F(a), F(b)) for a, b in points)
        h = hull(p)
        self.assertEqual(h, hull(tuple(reversed(p))+p))
        self.assertEqual(hull(h+p), h)
        self.assertTrue(set(h) <= set(p))

    def test_dimensions(self):
        self.assertEqual(dimension(hull(())), -1)
        self.assertEqual(dimension(hull(((F(0), F(0)),))), 0)
        self.assertEqual(dimension(hull(tuple((F(k), F(k)) for k in range(3)))), 1)
        self.assertEqual(dimension(hull(tuple((F(a), F(b)) for a, b in product((0, 1), repeat=2)))), 2)

    def test_empty_and_cap_fail_closed(self):
        a, b = matrices(Game())
        with self.assertRaises(ValueError):
            reconstruct(a, b, [])
        profiles, _ = audit(Game())
        with self.assertRaises(ValueError):
            reconstruct(a, b, profiles, cap=1)

    def test_invalid_profile(self):
        g = Game()
        with self.assertRaises(ValueError):
            reconstruct(*matrices(g), [(lift((F(1), F(1))), lift((F(0), F(0))))])

    def test_invalid_probability(self):
        for p in ((F(1),), (F(-1), F(1), F(0), F(1)), (F(0),)*4):
            with self.assertRaises(ValueError):
                project(p)
        with self.assertRaises(ValueError):
            lift((F(-1), F(0)))

    def test_negative_convex_hull(self):
        g = Game()
        # Joint convexification of all equilibria introduces a non-equilibrium.
        self.assertGreater(regret(*matrices(g), (F(1, 2),)*2, (F(1, 2),)*2), 0)

    def test_parser_mismatch(self):
        game = read_game(Game())
        game[1, 2][game.players[0]] = 99
        with patch('families.pygambit.read_nfg', return_value=game), self.assertRaises(ValueError):
            read_game(Game())

    def test_parser_dimensions(self):
        import pygambit
        game = pygambit.Game.new_table([2, 2])
        with patch('families.pygambit.read_nfg', return_value=game), self.assertRaises(ValueError):
            read_game(Game())


if __name__ == '__main__':
    unittest.main()
