from itertools import product
import unittest
import numpy as np
from src.epsilon_robustness import robust_regret


class RobustnessTests(unittest.TestCase):
    def test_zero_noise_matches_deviation_regret(self):
        A = ((1.0, -1.0), (-1.0, 1.0))
        p = (0.3, 0.7)
        q = (0.4, 0.6)
        got = robust_regret(A, p, q, 0.0)
        direct = max(
            0.0,
            *(
                sum(
                    q[j] * (A[a][j] - sum(p[i] * A[i][j] for i in range(2)))
                    for j in range(2)
                )
                for a in range(2)
            ),
        )
        self.assertAlmostEqual(got.robust_regret, direct, 14)

    def test_exact_against_all_box_vertices(self):
        rng = np.random.default_rng(4)
        for _ in range(60):
            A = rng.normal(size=(2, 2))
            p = np.array([0.27, 0.73])
            q = np.array([0.61, 0.39])
            d = 0.02
            got = robust_regret(A, p, q, d).robust_regret
            worst = 0.0
            for signs in product((-1.0, 1.0), repeat=4):
                U = A + d * np.array(signs).reshape(2, 2)
                baseline = sum(
                    p[i] * q[j] * U[i, j] for i, j in product(range(2), repeat=2)
                )
                for a in range(2):
                    worst = max(worst, sum(q[j] * U[a, j] for j in range(2)) - baseline)
            self.assertAlmostEqual(got, worst, 12)

    def test_symmetric_mixed_coordination_bound_is_delta(self):
        A = ((1.0, -1.0), (-1.0, 1.0))
        got = robust_regret(A, (0.5, 0.5), (0.5, 0.5), 0.03)
        self.assertAlmostEqual(got.nominal_regret, 0.0, 14)
        self.assertAlmostEqual(got.robust_regret, 0.03, 14)

    def test_reject_invalid(self):
        for args in [
            (((1.0,),), (0.5, 0.5), (0.5, 0.5), 0.0),
            (((1.0, 0.0), (0.0, 1.0)), (0.2, 0.2), (0.5, 0.5), 0.0),
            (((1.0, 0.0), (0.0, 1.0)), (0.5, 0.5), (0.5, 0.5), -1.0),
        ]:
            with self.assertRaises(ValueError):
                robust_regret(*args)
        with self.assertRaises(ValueError):
            robust_regret(
                ((1.0, 0.0), (0.0, 1.0)),
                (0.5, 0.5),
                (0.5, 0.5),
                float("inf"),
            )


if __name__ == "__main__":
    unittest.main()
