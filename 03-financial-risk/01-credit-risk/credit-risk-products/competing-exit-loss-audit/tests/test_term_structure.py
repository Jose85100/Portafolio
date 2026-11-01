import math
import random
import unittest

from src.affine import project_affine
from src.term_structure import project_term_structure


class TermTests(unittest.TestCase):
    def test_flat_force_reduces_to_affine(self):
        args=([.13,.37,.5],[.24]*3,[1.2]*3,[100.,90.,50.],[90.,70.,10.])
        old=project_affine(*args,discount_force=.06)
        new=project_term_structure(*args,[.06]*3)
        self.assertAlmostEqual(new.exact_loss,old.exact_loss,places=13)
        self.assertAlmostEqual(new.default_probability,old.default_probability,places=14)

    def test_discrete_payment_is_not_slope(self):
        discrete=project_term_structure([.5,.5],[.24]*2,[1.2]*2,[100.,20.],[100.,20.],[.06]*2)
        smooth=project_term_structure([.5,.5],[.24]*2,[1.2]*2,[100.,60.],[60.,20.],[.06]*2)
        self.assertGreater(abs(discrete.exact_loss-smooth.exact_loss),.1)
        self.assertAlmostEqual(discrete.exact_loss,discrete.midpoint_exposure_loss)

    def test_partition_and_mass_multiple_seeds(self):
        for seed in range(20):
            rng=random.Random(seed)
            d,p,r=[rng.uniform(0,2) for _ in range(3)]
            point=rng.uniform(.01,.99)
            original=project_term_structure([1.],[d],[p],[100.],[20.],[r])
            middle=100-80*point
            split=project_term_structure([point,1-point],[d]*2,[p]*2,[100.,middle],[middle,20.],[r]*2)
            self.assertAlmostEqual(original.exact_loss,split.exact_loss,places=12)
            self.assertAlmostEqual(split.default_probability+split.prepayment_probability+split.survival,1.)

    def test_zero_and_discount_monotonicity(self):
        args=([.2,.8],[.2]*2,[.3]*2,[100.,70.],[100.,70.])
        zero=project_term_structure(*args,[0.,0.])
        high=project_term_structure(*args,[.1,.3])
        self.assertGreater(zero.exact_loss,high.exact_loss)
        self.assertAlmostEqual(high.terminal_discount,math.exp(-.26))
        self.assertEqual(project_term_structure([1.],[0.],[0.],[100.],[100.],[0.]).exact_loss,0.)

    def test_invalid_and_tail_validation(self):
        for rates in ([],[-.1],[math.inf],[math.nan]):
            with self.assertRaises(ValueError):
                project_term_structure([1.],[.2],[.3],[100.],[100.],rates)
        with self.assertRaises(ValueError):
            project_term_structure([1.,1.],[1e4,.2],[0.,0.],[100.,100.],[100.,-1.],[0.,0.])
