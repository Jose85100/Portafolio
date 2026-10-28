import unittest

import numpy as np

from src.joint_gate import correct_covariance_joint
from src.moments import correct_covariance, population_covariance


class JointGateTests(unittest.TestCase):
    def test_regressor_gate_accepts_impossible_joint_model(self):
        for beta in [-1.0, 0.0, 0.3, 2.0]:
            s = population_covariance(beta)
            self.assertEqual(correct_covariance(s, 1.2).status, "accepted")
            self.assertEqual(
                correct_covariance_joint(s, 1.2).status, "incompatible_joint_covariance"
            )

    def test_valid_models_preserved_and_boundary_oracle(self):
        for beta in [-1.0, 0.0, 0.3, 2.0]:
            s = population_covariance(beta)
            self.assertAlmostEqual(
                correct_covariance_joint(s, 1).slope, beta, places=11
            )
            self.assertEqual(correct_covariance_joint(s, 178 / 153).status, "accepted")
            self.assertEqual(
                correct_covariance_joint(s, 1.5).status,
                correct_covariance(s, 1.5).status,
            )
            # False variance0.5 passes both checks: compatibility is not truth.
            self.assertGreater(abs(correct_covariance_joint(s, 0.5).slope - beta), 0.4)

    def test_units_and_independent_schur_oracle(self):
        rng = np.random.default_rng(20261028)
        for _ in range(20):
            beta = float(rng.normal())
            s = population_covariance(beta)
            a = s[np.ix_([0, 2], [0, 2])]
            b = s[1, [0, 2]]
            limit = float(s[1, 1] - b @ np.linalg.solve(a, b))
            for variance in [0.5, 1.0, 1.15, 1.2, 1.24]:
                expected = variance <= limit
                r = correct_covariance_joint(s, variance)
                self.assertEqual(r.status == "accepted", expected)
                d = np.diag([4.0, 2.0, 3.0])
                changed = correct_covariance_joint(d @ s @ d, variance * 4)
                self.assertEqual(r.status, changed.status)
                if r.slope is not None:
                    self.assertAlmostEqual(changed.slope, 3 * r.slope / 4, places=10)

    def test_invalid_tolerance_and_degenerate_y(self):
        with self.assertRaises(ValueError):
            correct_covariance_joint(np.eye(3), 0, tolerance=-1)
        with self.assertRaises(ValueError):
            correct_covariance_joint(np.eye(2), 0)
        self.assertEqual(
            correct_covariance_joint(np.diag([1.0, 1.0, -1.0]), 0).status,
            "incompatible_joint_covariance",
        )
        # Zero target variance with zero cross-covariances is valid PSD.
        self.assertEqual(
            correct_covariance_joint(np.diag([1.0, 1.0, 0.0]), 0).status, "accepted"
        )
