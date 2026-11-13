import itertools
import math
import unittest

from src.guard import ContaminationGuard


class TestGuard(unittest.TestCase):
    def test_oracle_and_identity(self):
        c = ContaminationGuard([1.0, 2.0, 2.0, 3.0], 1)
        self.assertEqual(c.p_value(2.0), 1.0)
        self.assertEqual(c.p_value(4.0), 0.25)
        self.assertEqual(ContaminationGuard([1.0, 2.0, 2.0, 3.0]).p_value(2.0), 0.8)

    def test_envelope_exhaustive(self):
        # Every clean sample, 0..2 arbitrary tied contaminants, all test scores.
        for clean in itertools.product([0.0, 1.0, 2.0], repeat=3):
            for count in range(3):
                for contaminants in itertools.product([-1.0, 1.0, 3.0], repeat=count):
                    full = list(clean + contaminants)
                    for bound in range(count, len(full)):
                        guard = ContaminationGuard(full, bound)
                        oracle = ContaminationGuard(clean)
                        for test in [-2.0, 0.0, 1.0, 2.0, 4.0]:
                            self.assertGreaterEqual(
                                guard.p_value(test) + 1e-12, oracle.p_value(test)
                            )

    def test_leave_one_out_superuniform_with_contamination(self):
        clean = [0.0, 1.0, 1.0, 2.0, 4.0]
        for contaminants in ([0.0, 0.0], [99.0, 99.0], [-1.0, 99.0]):
            ps = [
                ContaminationGuard(
                    clean[:i] + clean[i + 1 :] + contaminants, 2
                ).p_value(x)
                for i, x in enumerate(clean)
            ]
            for alpha in [0.2, 0.4, 0.6, 0.8]:
                self.assertLessEqual(
                    sum(p <= alpha for p in ps) / len(ps), alpha + 1e-12
                )

    def test_monotone_bound_and_score(self):
        for m in range(4):
            guard = ContaminationGuard([0.0, 1.0, 2.0, 3.0], m)
            ps = [guard.p_value(x) for x in range(6)]
            self.assertEqual(ps, sorted(ps, reverse=True))
        self.assertLessEqual(
            ContaminationGuard([0.0, 1.0, 2.0], 0).p_value(3.0),
            ContaminationGuard([0.0, 1.0, 2.0], 1).p_value(3.0),
        )

    def test_invalid_and_sparse(self):
        for scores in ([], [math.nan], [math.inf]):
            with self.assertRaises(ValueError):
                ContaminationGuard(scores)
        for m in (-1, 3):
            with self.assertRaises(ValueError):
                ContaminationGuard([0.0, 1.0, 2.0], m)
        for m in (True, 0.5):
            with self.assertRaises(TypeError):
                ContaminationGuard([0.0, 1.0], m)
        with self.assertRaises(ValueError):
            ContaminationGuard([0.0]).p_value(math.inf)
        with self.assertRaises(ValueError):
            ContaminationGuard([0.0]).alert(1.0, 0)
        self.assertFalse(ContaminationGuard([0.0] * 20, 19).alert(999.0, 0.05))
