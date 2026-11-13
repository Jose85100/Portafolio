import sys
import unittest
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.polyhedra import (Game, equilibrium_cells, exact_regret, player_region,
                          polygon, serialize_cell)


class PolyhedralTests(unittest.TestCase):
    def test_main_five_points(self):
        cells = equilibrium_cells(Game())
        self.assertEqual(len(cells), 5)
        self.assertTrue(all(c.dimension == 0 for c in cells))
        self.assertIn((F(0), F(25, 136), F(0), F(25, 136)), [c.vertices[0] for c in cells])

    def test_nontrivial_family(self):
        cells = equilibrium_cells(Game(accuracy=.5))
        self.assertEqual([c.dimension for c in cells], [0, 0, 2])
        self.assertEqual(len(cells[-1].vertices), 4)

    def test_total_indifference_box(self):
        cells = equilibrium_cells(Game(accuracy=.5, cost=.5, complementarity=0))
        self.assertEqual(len(cells), 1)
        self.assertEqual(cells[0].dimension, 4)
        self.assertEqual(len(cells[0].vertices), 16)

    def test_singular_support_not_family(self):
        cells = equilibrium_cells(Game(accuracy=1., cost=1.))
        self.assertEqual(len(cells), 2)
        self.assertTrue(all(c.dimension == 0 for c in cells))

    def test_empty_and_redundant_polygon(self):
        empty = polygon(((F(0), F(0), F(1)),), ())
        self.assertEqual(empty.dimension, -1)
        self.assertEqual(empty.vertices, ())
        line = polygon(((F(1), F(1), F(1)), (F(2), F(2), F(2))), ())
        self.assertEqual(line.dimension, 1)
        self.assertEqual(len(line.vertices), 2)

    def test_serialization(self):
        value = serialize_cell(equilibrium_cells(Game())[0])
        self.assertIn('vertices', value)
        self.assertEqual(value['dimension'], 0)

    def test_invalid(self):
        with self.assertRaises(ValueError): player_region(Game(), (0, 3), (0, 0))
        for point in ((F(0),), (F(2), F(0), F(0), F(0))):
            with self.assertRaises(ValueError): exact_regret(Game(), point)

    def test_pruning_preserves_containment(self):
        g = Game(accuracy=.5, cost=.5, complementarity=0)
        all_cells = equilibrium_cells(g, maximal=False)
        maximal = equilibrium_cells(g)
        self.assertTrue(all(any(c.contains_cell(d) for c in maximal) for d in all_cells))

    @settings(max_examples=20, derandomize=True, deadline=None)
    @given(st.integers(5, 10), st.integers(1, 15), st.integers(0, 12))
    def test_vertices_and_barycenters_equilibria(self, q, c, alpha):
        g = Game(accuracy=q/10, cost=c/10, complementarity=alpha/10)
        cells = equilibrium_cells(g)
        self.assertTrue(cells)
        for cell in cells:
            for vertex in cell.vertices:
                self.assertEqual(exact_regret(g, vertex), 0)
            barycenter = tuple(sum(v[i] for v in cell.vertices)/len(cell.vertices) for i in range(4))
            self.assertEqual(exact_regret(g, barycenter), 0)

    @settings(max_examples=50, derandomize=True)
    @given(st.integers(1, 9), st.integers(1, 9))
    def test_rectangle_dimension_property(self, a, b):
        region = polygon((), ((F(1), F(0), F(a, 10)), (F(0), F(1), F(b, 10))))
        self.assertEqual(region.dimension, 2)
        self.assertEqual(len(region.vertices), 4)
        np.testing.assert_allclose([float(max(v[0] for v in region.vertices)),
                                    float(max(v[1] for v in region.vertices))], [a/10, b/10])


if __name__ == '__main__':
    unittest.main()
