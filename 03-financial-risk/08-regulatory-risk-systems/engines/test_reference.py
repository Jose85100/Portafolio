import unittest
from reference import weighted_rwa, ecl, empirical_es, cash_path, operational_losses, kri_status

class NumericalContracts(unittest.TestCase):
    def test_rwa_manual_and_scale(self):
        self.assertEqual(weighted_rwa([100, 200], [0.5, 1]), 250)
        self.assertEqual(weighted_rwa([200, 400], [0.5, 1]), 500)

    def test_ecl_survival_not_sum_of_hazards(self):
        self.assertAlmostEqual(ecl([0.5, 0.5], [1, 1], [100, 100]), 75)
        self.assertAlmostEqual(ecl([1, 1], [1, 1], [100, 100]), 100)
        self.assertEqual(ecl([0], [1], [100]), 0)

    def test_discount(self):
        self.assertAlmostEqual(ecl([1], [0.5], [110], 0.1), 50)

    def test_fractional_tail_and_translation(self):
        self.assertAlmostEqual(empirical_es([1, 2, 3, 4], 0.625), 11 / 3)
        self.assertAlmostEqual(empirical_es([11, 12, 13, 14], 0.625), 41 / 3)
        self.assertEqual(empirical_es([1, 2, 3, 4], 0), 2.5)

    def test_cash_identity(self):
        self.assertEqual(cash_path(100, [-80, -30, 50]), [100, 20, -10, 40])

    def test_operational_zero_seed_and_mean(self):
        self.assertEqual(operational_losses(0, 10, 3), [0, 0, 0])
        self.assertEqual(operational_losses(2, 10, 5, 1), operational_losses(2, 10, 5, 1))
        sample = operational_losses(2, 10, 20000, 41)
        self.assertLess(abs(sum(sample) / len(sample) - 20), 1)

    def test_kri_direction_missing_and_boundaries(self):
        self.assertEqual(kri_status(None, 5, 10), "unknown")
        self.assertEqual(kri_status(10, 5, 10), "breach")
        self.assertEqual(kri_status(5, 5, 10), "warning")
        self.assertEqual(kri_status(2, 5, 3, False), "breach")

    def test_invalid_contracts(self):
        cases = [
            lambda: weighted_rwa([1], []),
            lambda: weighted_rwa([-1], [1]),
            lambda: ecl([1.1], [1], [1]),
            lambda: ecl([1], [1], [1], -1),
            lambda: empirical_es([1], 1),
            lambda: empirical_es([float("nan")]),
            lambda: cash_path(1, [float("inf")]),
            lambda: operational_losses(1, 1, 0),
            lambda: kri_status(1, 10, 5),
        ]
        for case in cases:
            with self.assertRaises(ValueError):
                case()

if __name__ == "__main__":
    unittest.main()
