import unittest

from scipy.stats import beta

from src.coattendance_gate import (
    PlanCount,
    binomial_lower_oracle,
    clopper_pearson_lower,
    exact_lower_coverage,
    hoeffding_lower,
    select_plan,
    simultaneous_bounds,
)


class CoattendanceGateTests(unittest.TestCase):
    def setUp(self):
        self.plans = [PlanCount("A", 1, 110, 200), PlanCount("B", 2, 130, 200),
                      PlanCount("C", 3, 150, 200)]

    def test_predeclared_menu_has_same_family_error_budget(self):
        cp = simultaneous_bounds(self.plans, .05, "clopper_pearson")
        hoeffding = simultaneous_bounds(self.plans, .05, "hoeffding")
        self.assertEqual([x["alpha_each"] for x in cp], [.05/3]*3)
        self.assertAlmostEqual(cp[1]["lower"], .5736297217395927, places=12)
        self.assertAlmostEqual(hoeffding[1]["lower"], .5488275659798814, places=12)

    def test_method_changes_selected_plan_under_fixed_cost_menu(self):
        self.assertEqual(select_plan(self.plans, .56, .05, "clopper_pearson"), "B")
        self.assertEqual(select_plan(self.plans, .56, .05, "hoeffding"), "C")

    def test_abstains_instead_of_clipping_or_changing_target(self):
        tiny = [PlanCount("tiny", 0, 0, 10)]
        self.assertLess(hoeffding_lower(0, 10, .05), 0)
        with self.assertRaisesRegex(ValueError, "abstain"):
            select_plan(tiny, .01, .05, "hoeffding")

    def test_cp_matches_independent_binomial_tail_inversion(self):
        for n, x, alpha in ((10, 3, .01), (30, 19, .025), (200, 130, .05/3)):
            self.assertAlmostEqual(clopper_pearson_lower(x, n, alpha),
                                   binomial_lower_oracle(x, n, alpha), places=10)

    def test_cp_matches_beta_quantile_and_boundary_cases(self):
        self.assertEqual(clopper_pearson_lower(0, 20, .05), 0.0)
        self.assertAlmostEqual(clopper_pearson_lower(20, 20, .05), beta.ppf(.05, 20, 1))
        self.assertEqual(exact_lower_coverage(20, 0.0, .05, "clopper_pearson"), 1.0)
        self.assertEqual(exact_lower_coverage(20, 1.0, .05, "clopper_pearson"), 1.0)

    def test_cp_coverage_is_at_least_nominal_on_small_exact_grid(self):
        for n in (5, 10, 30, 100):
            for p in (0.1, 0.25, 0.5, 0.7, 0.9):
                coverage = exact_lower_coverage(n, p, .05, "clopper_pearson")
                self.assertGreaterEqual(coverage + 1e-12, .95)

    def test_validation_rejects_bad_inputs_and_duplicate_menu(self):
        for args in (("", 0, 0, 1), ("A", -1, 0, 1), ("A", 1, -1, 1),
                     ("A", 1, 2, 1), ("A", 1, True, 1), ("A", 1, 0, 0)):
            with self.assertRaises(ValueError):
                PlanCount(*args)
        with self.assertRaises(ValueError):
            simultaneous_bounds([self.plans[0], self.plans[0]], .05, "clopper_pearson")
        for method in ("normal", "" ):
            with self.assertRaises(ValueError):
                simultaneous_bounds(self.plans, .05, method)
        for alpha in (0, 1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                clopper_pearson_lower(1, 2, alpha)

    def test_hypothesis_selection_uses_cheapest_passing_plan(self):
        self.assertEqual(select_plan(self.plans, .4, .05, "clopper_pearson"), "A")
        self.assertEqual(select_plan(self.plans, .65, .05, "clopper_pearson"), "C")
        with self.assertRaises(ValueError):
            select_plan(self.plans, .999, .05, "clopper_pearson")


if __name__ == "__main__":
    unittest.main()
