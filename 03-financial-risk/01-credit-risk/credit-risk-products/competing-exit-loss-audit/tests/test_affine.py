import math
import random
import unittest
from decimal import Decimal, localcontext

from src.affine import discounted_mean_fraction, project_affine
from src.calendar import project_calendar


class AffineTests(unittest.TestCase):
    def test_constant_reduces_to_original(self):
        args = ([.13,.87], [.2,.3], [.9,.1], [100.,70.])
        old = project_calendar(*args)
        new = project_affine(*args, [100.,70.])
        self.assertAlmostEqual(old.exact_loss, new.exact_loss, places=13)
        self.assertAlmostEqual(new.default_probability+new.prepayment_probability+new.survival,1.)

    def test_partition_invariance_irregular(self):
        one = project_affine([1.],[.24],[1.2],[100.],[20.])
        dt = [.03,.17,.31,.49]
        edges = [0.,.03,.2,.51,1.]
        split = project_affine(dt,[.24]*4,[1.2]*4,
                               [100-80*t for t in edges[:-1]],
                               [100-80*t for t in edges[1:]])
        self.assertAlmostEqual(one.exact_loss,split.exact_loss,places=13)

    def test_decimal_oracle_small_large(self):
        with localcontext() as ctx:
            ctx.prec = 75
            for text in ['1e-12','1e-6','.009','.01','1','10','1000']:
                x = Decimal(text)
                expected = Decimal(1)/x - Decimal(1)/(x.exp()-1)
                self.assertLess(abs(discounted_mean_fraction(float(x))-float(expected)),2e-14)

    def test_properties_multiple_seeds(self):
        for seed in range(10):
            rng = random.Random(seed)
            for _ in range(20):
                start,end = sorted([rng.uniform(0,200),rng.uniform(0,200)],reverse=True)
                r = project_affine([rng.uniform(.01,5)],[rng.uniform(0,2)],
                                   [rng.uniform(0,2)],[start],[end])
                self.assertLessEqual(r.endpoint_loss,r.exact_loss+1e-12)
                self.assertLessEqual(r.midpoint_loss,r.exact_loss+1e-12)
                self.assertLessEqual(r.exact_loss,r.constant_start_loss+1e-12)

    def test_negative_direction_and_zero(self):
        r = project_affine([1.],[.24],[1.2],[20.],[100.])
        self.assertGreater(r.endpoint_loss,r.exact_loss)
        self.assertGreater(r.midpoint_loss,r.exact_loss)
        self.assertEqual(project_affine([1.],[0.],[1.],[100.],[0.]).exact_loss,0.)
        self.assertEqual(discounted_mean_fraction(0.),.5)

    def test_invalid(self):
        for end in ([],[-1.],[math.nan],[math.inf]):
            with self.assertRaises(ValueError):
                project_affine([1.],[.2],[.3],[100.],end)
        for x in (-1.,math.inf,math.nan):
            with self.assertRaises(ValueError):
                discounted_mean_fraction(x)
