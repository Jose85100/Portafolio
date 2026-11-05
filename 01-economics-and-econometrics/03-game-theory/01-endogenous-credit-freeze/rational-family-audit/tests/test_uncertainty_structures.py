import itertools
import unittest

from src.uncertainty_structures import shared_opponent_shock_regret
from src.epsilon_robustness import robust_regret


class SharedShockTests(unittest.TestCase):
    def test_shared_opponent_shocks_cancel_at_all_box_vertices(self):
        a=[[1.0,-1.0],[-0.4,0.7]]; p=[0.3,0.7]; q=[0.6,0.4]; d=0.2
        target=shared_opponent_shock_regret(a,p,q,d)
        values=[]
        for x,y in itertools.product((-d,d), repeat=2):
            shifted=[[a[i][j]+(x,y)[j] for j in range(2)] for i in range(2)]
            values.append(robust_regret(shifted,p,q,0).robust_regret)
        self.assertAlmostEqual(target, max(values), places=12)
        self.assertTrue(all(abs(v-target)<1e-12 for v in values))

    def test_independent_cell_error_is_not_weaker_than_shared_shock(self):
        a=[[1.0,-1.0],[-0.4,0.7]]; p=[0.3,0.7]; q=[0.6,0.4]; d=0.2
        self.assertGreaterEqual(robust_regret(a,p,q,d).robust_regret,
                                shared_opponent_shock_regret(a,p,q,d))


if __name__ == "__main__": unittest.main()
