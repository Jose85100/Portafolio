import unittest
from math import comb
from src.quorum import Regime,add_standbys,choose,exact,independent_marginals


def sample():
    return [Regime('normal',.8,(.95,1,1,1)),Regime('shock',.2,(.95,0,0,0))]


class QuorumTests(unittest.TestCase):
    def test_closed_form_common_cause(self):
        self.assertAlmostEqual(exact(sample(),3,(0,))['available'],.95*.8)
        self.assertAlmostEqual(exact(add_standbys(sample(),2,.9),3,(0,))['available'],.95*(.8+.2*.9**2))
        self.assertAlmostEqual(independent_marginals(sample(),3,(0,))['available'],.95*(3*.8**2*.2+.8**3))

    def test_binomial_oracle_and_total_mass(self):
        for n in range(1,7):
            result=exact([Regime('one',1,(.7,)*n)],max(1,n//2),())
            oracle=sum(comb(n,k)*.7**k*.3**(n-k) for k in range(max(1,n//2),n+1))
            self.assertAlmostEqual(result['available'],oracle)
            self.assertAlmostEqual(result['total_mass'],1)

    def test_mandatory_and_deterministic(self):
        self.assertEqual(exact([Regime('one',1,(0,1,1))],2,(0,))['available'],0)
        self.assertEqual(exact([Regime('one',1,(1,1,1))],3,(0,))['available'],1)
        self.assertLessEqual(exact(add_standbys(sample(),2,.9),3,(0,))['available'],.95)

    def test_false_pass_and_infeasible(self):
        args=(sample(),3,(0,),[0,1,2],.9,1,.85)
        self.assertEqual(choose(*args)['standbys'],2)
        self.assertEqual(choose(*args,independent=True)['standbys'],0)
        with self.assertRaises(ValueError):
            choose(sample(),3,(0,),[0,1,2],.9,1,.97)
        with self.assertRaises(ValueError):
            choose(sample(),4,(0,),[0,1,2],.9,1,.85)

    def test_invalid(self):
        for regimes,q,m in (([],1,()),([Regime('one',1,())],1,()),(sample(),0,()),(sample(),3,(7,)),(sample(),3,(0,0)),([Regime('x',.5,(.1,))],1,()),([Regime('x',1,(2,))],1,()),([Regime('x',1,(1,)*17)],1,())):
            with self.assertRaises(ValueError):
                exact(regimes,q,m)
        with self.assertRaises(ValueError):
            exact([Regime('x',.5,(1,)),Regime('x',.5,(1,))],1,())
        with self.assertRaises(ValueError):
            add_standbys(sample(),-1,.9)
        with self.assertRaises(ValueError):
            choose(sample(),3,(0,),[],.9,1,.85)
