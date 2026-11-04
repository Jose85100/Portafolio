import math
import unittest
from decimal import Decimal, localcontext
from src.lgd_uncertainty import Scenario, evaluate, _exp_moment

class MomentsTests(unittest.TestCase):
    def test_constant_ead_and_zero_prepay(self):
        s=Scenario(100,100,2,.2,0,2,3)
        x=evaluate(s)
        self.assertAlmostEqual(x.default_probability,1-math.exp(-.4),places=14)
        self.assertGreater(x.loss_variance,x.plugin_variance)
    def test_beta_degenerate_limit_variance_removed(self):
        s=Scenario(10,30,1,.3,.2,1e9,1e9)
        x=evaluate(s)
        self.assertLess(x.lgd_variance,1e-9)
        self.assertAlmostEqual(x.loss_variance,x.plugin_variance,delta=1e-7)
    def test_zero_default_hazard(self):
        x=evaluate(Scenario(10,20,1,0,.5,2,2))
        self.assertEqual(x.default_probability,0)
        self.assertEqual(x.expected_loss,0)
    def test_exponential_integrals_match_limits(self):
        self.assertAlmostEqual(_exp_moment(0,2,2),8/3)
        self.assertAlmostEqual(_exp_moment(1e-9,1,0),1-0.5e-9,places=12)
        self.assertAlmostEqual(_exp_moment(1e-9,1,1),.5-1e-9/3,places=12)
        self.assertAlmostEqual(_exp_moment(1e-9,1,2),1/3-1e-9/4,places=12)
    def test_exp_moment_near_series_boundary_against_decimal(self):
        with localcontext() as ctx:
            ctx.prec = 60
            for x in (Decimal("0.001"), Decimal("0.0011"), Decimal("0.002"), Decimal("0.499"), Decimal("0.5")):
                for k in (0, 1, 2):
                    exact = Decimal(math.factorial(k)) / x**(k+1) * (Decimal(1) - (-x).exp() * sum(x**j / Decimal(math.factorial(j)) for j in range(k+1)))
                    got = _exp_moment(float(x), 1.0, k)
                    rel = abs(Decimal(str(got)) - exact) / abs(exact)
                    self.assertLess(float(rel), 2e-12, (x,k,rel))

    def test_input_validation(self):
        with self.assertRaises(ValueError): evaluate(Scenario(-1,2,1,.2,.1,2,2))

if __name__ == '__main__': unittest.main()
