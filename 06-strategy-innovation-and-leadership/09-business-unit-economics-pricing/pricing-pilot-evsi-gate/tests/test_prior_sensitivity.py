import unittest
from evsi import Price
from prior_sensitivity import concentration_grid


class PriorSensitivityTests(unittest.TestCase):
    def test_means_preserved_evsi_tends_down_with_concentration(self):
        p = [Price("A",100,11,9), Price("B",180,5,15)]
        rows = concentration_grid(p, 20, 1, [0.25, 1, 4])
        self.assertTrue(all(b["evsi"] <= a["evsi"] + 1e-12 for a,b in zip(rows,rows[1:])))
        self.assertAlmostEqual(rows[0]["baseline_value"], rows[-1]["baseline_value"])

    def test_expected_value_converges_to_baseline_at_high_concentration(self):
        p = [Price("A",100,11,9), Price("B",180,5,15)]
        rows = concentration_grid(p, 20, 1, [1,1000])
        self.assertLess(rows[-1]["evsi"], rows[0]["evsi"])

    def test_high_concentration_negative_residual_is_reported(self):
        p = [Price("A",100,11,9), Price("B",180,5,15)]
        row = concentration_grid(p,20,1,[100])[0]
        self.assertGreaterEqual(row["evsi"], -row["roundoff_bound"])
        self.assertTrue(row["evsi_negative_roundoff"])

    def test_nonpositive_concentration_rejected(self):
        with self.assertRaises(ValueError): concentration_grid([Price("A",1,1,1),Price("B",2,1,1)],1,0,[0])

    def test_pilot_cost_can_reverse_gate_without_changing_evsi(self):
        p = [Price("A",100,11,9), Price("B",180,5,15)]
        a = concentration_grid(p,20,0,[1])[0]
        b = concentration_grid(p,20,5,[1])[0]
        self.assertEqual(a["evsi"],b["evsi"])
        self.assertNotEqual(a["decision"],b["decision"])

if __name__ == "__main__": unittest.main()
