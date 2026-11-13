import importlib.util
import pathlib
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / "src" / "validation.py"
SPEC = importlib.util.spec_from_file_location("credit_validation", SOURCE)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class CreditValidationTests(unittest.TestCase):
    def test_perfect_discrimination(self):
        self.assertEqual(module.auc_gini([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]), (1.0, 1.0))
        self.assertEqual(module.ks_statistic([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]), 1.0)

    def test_tied_scores_and_brier(self):
        self.assertEqual(module.auc_gini([0, 1], [0.5, 0.5]), (0.5, 0.0))
        self.assertEqual(module.ks_statistic([0, 1], [0.5, 0.5]), 0.0)
        self.assertAlmostEqual(module.brier_score([0, 1], [0.2, 0.8]), 0.04)

    def test_single_class_rejected(self):
        with self.assertRaises(ValueError):
            module.auc_gini([1, 1], [0.3, 0.4])
        with self.assertRaises(ValueError):
            module.ks_statistic([0, 0], [0.3, 0.4])

    def test_psi_identity_and_shift(self):
        edge = [0, 0.5, 1]
        self.assertAlmostEqual(module.population_stability_index([0.1, 0.9], [0.1, 0.9], edge), 0)
        self.assertGreater(module.population_stability_index([0.1] * 30, [0.9] * 30, edge), 0)

    def test_psi_bad_edges(self):
        with self.assertRaises(ValueError):
            module.population_stability_index([0.2], [0.2], [0.1, 0.5])

    def test_hazard_ecl_not_cumulative(self):
        observed = module.ecl_from_conditional_hazards([0.1, 0.2], [0.5, 0.5],
                                                       [100, 100], [1, 1])
        self.assertAlmostEqual(observed, 14.0)

    def test_ecl_bounds(self):
        self.assertEqual(module.ecl_from_conditional_hazards([0, 0], [1, 1], [100, 100], [1, 1]), 0)
        with self.assertRaises(ValueError):
            module.ecl_from_conditional_hazards([0.1], [1], [-1], [1])

    def test_scenario_weights(self):
        self.assertAlmostEqual(module.scenario_weighted_ecl([(0.8, 10), (0.2, 30)]), 14)
        with self.assertRaises(ValueError):
            module.scenario_weighted_ecl([(0.7, 10), (0.2, 30)])


if __name__ == "__main__":
    unittest.main()
