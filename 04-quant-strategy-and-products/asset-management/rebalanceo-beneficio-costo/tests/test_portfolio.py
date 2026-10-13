import unittest
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

from src.portfolio import Config, backtest, decide, metrics, minimum_variance, simulate


class PortfolioTests(unittest.TestCase):
    def test_analytic_diagonal(self):
        c = np.diag([1.0, 4.0, 9.0]) * 1e-5
        expected = 1 / np.diag(c)
        expected /= expected.sum()
        np.testing.assert_allclose(minimum_variance(c), expected, atol=2e-6)

    def test_scale_invariance(self):
        c = np.diag([1.0, 4.0, 9.0])
        for scale in [1e-8, 1e-4, 1.0, 1e4]:
            np.testing.assert_allclose(
                minimum_variance(c * scale), minimum_variance(c), atol=1e-6
            )

    def test_random_psd_properties(self):
        rng = np.random.default_rng(777)
        for n in [2, 5, 10]:
            for _ in range(10):
                a = rng.normal(size=(n, n))
                c = a @ a.T + np.eye(n) * 0.01
                w = minimum_variance(c)
                self.assertAlmostEqual(w.sum(), 1.0)
                self.assertGreaterEqual(w.min(), -1e-8)
                self.assertLessEqual(
                    w @ c @ w, np.full(n, 1 / n) @ c @ np.full(n, 1 / n) + 1e-7
                )

    def test_invalid_covariance(self):
        for c in [
            np.array([1, 2]),
            np.eye(1),
            np.array([[1, 2], [0, 1]]),
            np.diag([1, -1]),
            np.full((2, 2), np.nan),
        ]:
            with self.assertRaises(ValueError):
                minimum_variance(c)

    def test_solver_failure(self):
        with (
            patch(
                "src.portfolio.minimize",
                return_value=SimpleNamespace(success=False, message="failure"),
            ),
            self.assertRaises(RuntimeError),
        ):
            minimum_variance(np.eye(2))

    def test_zero_covariance(self):
        np.testing.assert_allclose(minimum_variance(np.zeros((2, 2))), [0.5, 0.5])

    def test_gate_economics(self):
        c = np.diag([0.01, 0.0001])
        self.assertTrue(
            decide(np.array([1.0, 0]), np.array([0.0, 1]), c, Config(cost_bps=0))[0]
        )
        self.assertFalse(
            decide(np.array([0.5, 0.5]), np.array([0.5, 0.5]), c, Config())[0]
        )
        self.assertFalse(
            decide(np.array([1.0, 0]), np.array([0.0, 1]), c, Config(cost_bps=10000))[0]
        )

    def test_no_lookahead(self):
        r = simulate(days=600)
        mutated = r.copy()
        mutated[400:] *= 2
        for s in [
            "equal",
            "legacy_mv",
            "monthly_mv",
            "static_mv",
            "gate",
            "gate_no_shrink",
        ]:
            x, y = backtest(r, s), backtest(mutated, s)
            np.testing.assert_array_equal(x["weights"][:149], y["weights"][:149])
            np.testing.assert_array_equal(x["net"][:148], y["net"][:148])

    def test_accounting_and_drift(self):
        r = np.array([[0.01, 0.0], [0.0, 0.0], [0.1, 0.0], [0.0, 0.1], [0.0, 0.0]])
        out = backtest(r, "equal", Config(window=2, step=2, cost_bps=10))
        self.assertAlmostEqual(out["net"][0], 0.05)
        np.testing.assert_allclose(out["weights"][1], [1.1 / 2.1, 1 / 2.1])
        np.testing.assert_allclose(
            out["net"], (1 - out["costs"]) * (1 + out["gross"]) - 1
        )

    def test_zero_cost_ablation(self):
        r = simulate(days=600)
        x = backtest(r, "monthly_mv", Config(cost_bps=0))
        y = backtest(r, "gate_no_shrink", Config(cost_bps=0))
        np.testing.assert_allclose(x["net"], y["net"], atol=1e-10)

    def test_invalid_inputs(self):
        for kwargs in [
            {"window": 1},
            {"step": 0},
            {"cost_bps": -1},
            {"gamma": 0},
            {"shrink": 2},
            {"cost_bps": np.nan},
        ]:
            with self.assertRaises(ValueError):
                Config(**kwargs)
        for r, s in [
            (np.zeros((2, 2)), "equal"),
            (np.zeros((300, 2)), "bad"),
            (np.full((300, 2), -1), "equal"),
            (np.full((300, 2), np.nan), "equal"),
        ]:
            with self.assertRaises(ValueError):
                backtest(r, s)
        with self.assertRaises(ValueError):
            simulate(days=10)

    def test_all_strategies_finite(self):
        for regime in ["stationary", "switch"]:
            r = simulate(days=600, regime=regime)
            for s in [
                "equal",
                "legacy_mv",
                "static_mv",
                "monthly_mv",
                "gate",
                "gate_no_shrink",
            ]:
                out = backtest(r, s)
                self.assertTrue(np.isfinite(list(metrics(out).values())).all())
                np.testing.assert_allclose(out["weights"].sum(axis=1), 1)

    def test_initial_drawdown(self):
        out = {
            "net": np.array([-0.1, 0]),
            "turnover": np.zeros(2),
            "costs": np.zeros(2),
        }
        self.assertAlmostEqual(metrics(out)["max_drawdown"], -0.1)


if __name__ == "__main__":
    unittest.main()
