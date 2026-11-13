from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import numpy as np
from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from clearing import Network, assets, bracket, residual_only, lp_clear, rational_clear, accounting, step


def ring(anchor=.1):
    return Network(np.array([[0., 1-anchor, 0], [0, 0, 1-anchor], [1-anchor, 0, 0]]), np.full(3, anchor))


class ClearingTests(unittest.TestCase):
    def test_sovereign_ring(self):
        net = ring()
        x = assets(net, np.array([0., .1, .1]), np.array([.1, 0, 0]), 1.)
        result = bracket(net, x)
        oracle = np.array(rational_clear(net, x), float)
        np.testing.assert_allclose(result.payments, oracle, atol=1e-8)
        np.testing.assert_allclose(lp_clear(net, x), oracle, atol=1e-8)
        a = accounting(net, x, result.payments)
        self.assertAlmostEqual(a['gross_unpaid'], 1., places=7)
        self.assertAlmostEqual(a['outside_unpaid'], .1, places=8)
        self.assertLess(abs(a['resource_identity_error']), 1e-8)

    @settings(max_examples=30, derandomize=True, deadline=None)
    @given(st.lists(st.integers(0, 9), min_size=9, max_size=9),
           st.lists(st.integers(0, 9), min_size=3, max_size=3))
    def test_oracles_and_enclosure(self, entries, resources):
        debt = np.array(entries, float).reshape(3, 3)/10
        np.fill_diagonal(debt, 0)
        net = Network(debt, np.full(3, .2))
        x = np.array(resources, float)/10
        r = bracket(net, x)
        exact = np.array(rational_clear(net, x), float)
        self.assertTrue((exact >= r.lower-1e-12).all())
        self.assertTrue((exact <= r.upper+1e-12).all())
        self.assertLessEqual(np.abs(r.payments-exact).sum(), r.width_l1+1e-12)
        np.testing.assert_allclose(lp_clear(net, x), exact, atol=1e-7)

    @settings(max_examples=30, derandomize=True, deadline=None)
    @given(st.floats(0., 1., allow_nan=False, allow_infinity=False))
    def test_shock_monotonicity(self, h):
        net = ring()
        base = assets(net, np.zeros(3), np.full(3, .1), 0)
        shock = assets(net, np.zeros(3), np.full(3, .1), h)
        self.assertTrue((bracket(net, shock).payments <= bracket(net, base).payments+1e-8).all())

    def test_near_closed_negative(self):
        net = ring(1e-9)
        x = np.full(3, 5e-10)
        old = residual_only(net, x)
        truth = np.array(rational_clear(net, x), float)
        self.assertEqual(old.iterations, 1)
        self.assertGreater(np.abs(old.payments-truth).sum(), 1.)
        with self.assertRaises(RuntimeError):
            bracket(net, x, max_iterations=100)

    def test_zero_debt_and_no_network(self):
        net = Network(np.zeros((2, 2)), np.array([0., 1.]))
        result = bracket(net, np.array([2., .3]))
        np.testing.assert_equal(result.payments, [0., .3])
        self.assertEqual(rational_clear(net, np.array([2., .3]))[0], 0)

    def test_bad_network(self):
        for debt, o in [(np.zeros((0, 0)), np.array([])), (np.eye(2), np.ones(2)),
                     (np.array([[0, -1], [0, 0]]), np.ones(2)),
                     (np.full((2, 2), np.nan), np.ones(2)),
                     (np.ones((2, 3)), np.ones(2)), (np.zeros((2, 2)), np.array([1, -1])),
                     (np.array([[0, 1], [1, 0]]), np.zeros(2)),
                     (np.array([[0, 1.], [1, 0]]), np.full(2, 1e-20))]:
            with self.assertRaises(ValueError):
                Network(debt, o)

    def test_bad_vectors_and_controls(self):
        net = ring()
        for bad in (np.array([1.]), np.array([-1., 0, 0]), np.array([np.inf, 0, 0])):
            with self.assertRaises(ValueError):
                bracket(net, bad)
        for h in (-1, 2, float('nan')):
            with self.assertRaises(ValueError):
                assets(net, np.zeros(3), np.ones(3), h)
        for kwargs in (dict(tolerance=0), dict(tolerance=float('nan')), dict(max_iterations=0)):
            for fn in (bracket, residual_only):
                with self.assertRaises(ValueError):
                    fn(net, np.ones(3), **kwargs)
        with self.assertRaises(ValueError):
            accounting(net, np.zeros(3), np.ones(3)*2)

    def test_lp_failure_not_solution(self):
        with patch('clearing.linprog', return_value=SimpleNamespace(success=False, x=None, message='test failure')):
            with self.assertRaises(RuntimeError):
                lp_clear(ring(), np.zeros(3))

    def test_rational_cap(self):
        with self.assertRaises(ValueError):
            rational_clear(Network(np.zeros((7, 7)), np.ones(7)), np.zeros(7))

    def test_reference_iteration(self):
        net = ring()
        x = np.array([0., .1, .1])
        r = residual_only(net, x)
        self.assertLess(np.abs(step(net, x, r.payments)-r.payments).sum(), 1e-7)
        with self.assertRaises(RuntimeError):
            residual_only(net, x, tolerance=1e-15, max_iterations=1)


if __name__ == '__main__':
    unittest.main()
