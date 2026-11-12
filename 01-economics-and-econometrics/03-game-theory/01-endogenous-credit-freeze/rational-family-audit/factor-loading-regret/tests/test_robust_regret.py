import unittest
from itertools import product

from src.robust_regret import factor_loading_regret, nominal_regret, rectangular_cell_regret


class RegretTests(unittest.TestCase):
    def setUp(self) -> None:
        self.a = ((1.0, -1.0), (-0.4, 0.7))
        self.p = (0.3, 0.7)
        self.q = (0.6, 0.4)

    def test_equal_loadings_cancel(self) -> None:
        self.assertAlmostEqual(factor_loading_regret(self.a, self.p, self.q, (4.0, 4.0), 0.5), nominal_regret(self.a, self.p, self.q))

    def test_heterogeneous_loading_exact_support(self) -> None:
        base = nominal_regret(self.a, self.p, self.q)
        value = factor_loading_regret(self.a, self.p, self.q, (0.0, 1.0), 0.2)
        self.assertAlmostEqual(value, base + 0.2 * 0.7)

    def test_matches_independent_vertex_oracle(self) -> None:
        loadings = (0.0, 1.0)
        delta = 0.2
        corner_regrets = []
        for factors in product((-delta, delta), repeat=2):
            perturbed = tuple(
                tuple(self.a[i][j] + loadings[i] * factors[j] for j in range(2))
                for i in range(2)
            )
            corner_regrets.append(nominal_regret(perturbed, self.p, self.q))
        self.assertAlmostEqual(
            factor_loading_regret(self.a, self.p, self.q, loadings, delta),
            max(corner_regrets),
        )

    def test_rectangular_baseline_is_more_conservative(self) -> None:
        self.assertGreater(rectangular_cell_regret(self.a, self.p, self.q, 0.2), factor_loading_regret(self.a, self.p, self.q, (0.0, 1.0), 0.2))

    def test_invalid_inputs_rejected(self) -> None:
        with self.assertRaises(ValueError):
            factor_loading_regret(self.a, (0.3, 0.8), self.q, (0.0, 1.0), 0.1)
        with self.assertRaises(ValueError):
            factor_loading_regret(self.a, self.p, self.q, (0.0, 1.0), -0.1)


if __name__ == "__main__":
    unittest.main()
