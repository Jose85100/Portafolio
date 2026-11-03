import math
import random
import unittest
from decimal import Decimal, localcontext

from src.affine import discounted_mean_fraction
from src.affine_lgd import project_loss_path, second_fraction_moment
from src.term_structure import project_term_structure


class LossPathTests(unittest.TestCase):
    def test_constant_lgd_recovers_prior_engine(self):
        args=([.13,.37,.5],[.24]*3,[1.2]*3,[100.,80.,20.],[90.,70.,10.])
        old=project_term_structure(*args,[.02,.08,.16],.45)
        new=project_loss_path(*args,[.45]*3,[.45]*3,[.02,.08,.16])
        self.assertAlmostEqual(old.exact_loss,new.exact_loss,places=13)
        self.assertAlmostEqual(new.exact_loss,new.product_of_means_loss,places=13)

    def test_moment_decimal_oracle(self):
        with localcontext() as ctx:
            ctx.prec=90
            for text in ['1e-12','.01','.499','.5','1','10','700','701']:
                x=Decimal(text)
                expected=2/x/x-(1+2/x)/(x.exp()-1)
                self.assertLess(abs(second_fraction_moment(float(x))-float(expected)),2e-14)
        self.assertAlmostEqual(second_fraction_moment(0.),1/3)

    def test_covariance_identity_and_negative_direction(self):
        x=1.5;m1=discounted_mean_fraction(x);m2=second_fraction_moment(x)
        for l0,l1 in [(.8,.2),(.2,.8),(.45,.45)]:
            result=project_loss_path([1.],[.24],[1.2],[100.],[20.],[l0],[l1],[.06])
            weight=.24/1.5*(-math.expm1(-1.5))
            difference=weight*(-80)*(l1-l0)*(m2-m1*m1)
            self.assertAlmostEqual(result.exact_loss-result.product_of_means_loss,difference,places=13)

    def test_partition_properties_multi_seed(self):
        for seed in range(20):
            rng=random.Random(seed);t=rng.uniform(.01,.99)
            e0,e1=[rng.uniform(0,200) for _ in range(2)]
            l0,l1=[rng.random() for _ in range(2)]
            one=project_loss_path([1.],[.24],[1.2],[e0],[e1],[l0],[l1],[.06])
            em=(1-t)*e0+t*e1;lm=(1-t)*l0+t*l1
            split=project_loss_path([t,1-t],[.24]*2,[1.2]*2,[e0,em],[em,e1],[l0,lm],[lm,l1],[.06]*2)
            self.assertAlmostEqual(one.exact_loss,split.exact_loss,places=12)
            self.assertGreaterEqual(one.exact_loss,0.)
            self.assertLessEqual(one.exact_loss,max(e0,e1)*one.default_probability+1e-12)
            self.assertAlmostEqual(one.default_probability+one.prepayment_probability+one.survival,1.)

    def test_zero_and_invalid(self):
        self.assertEqual(project_loss_path([1.],[0.],[0.],[100.],[20.],[.8],[.2],[0.]).exact_loss,0.)
        for lgd in ([],[-.01],[1.01],[math.nan]):
            with self.assertRaises(ValueError):project_loss_path([1.],[.24],[1.2],[100.],[20.],lgd,[.2],[.06])
        for exposure in ([-1.],[math.inf]):
            with self.assertRaises(ValueError):project_loss_path([1.],[.24],[1.2],exposure,[20.],[.8],[.2],[.06])
        for x in (-1.,math.inf,math.nan):
            with self.assertRaises(ValueError):second_fraction_moment(x)
