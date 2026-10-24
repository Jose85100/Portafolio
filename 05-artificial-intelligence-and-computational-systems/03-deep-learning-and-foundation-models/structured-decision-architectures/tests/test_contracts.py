import unittest
import numpy as np
from src.contracts import Decision, Evidence, choose_action, select_threshold, extract_literal


class Contracts(unittest.TestCase):
    def test_decision(self):
        self.assertEqual(Decision(('a','b'),(.2,.8),'fixture-1').model_version,'fixture-1')
        for labels,p in [(('a','a'),(.2,.8)),(('a','b'),(.2,.7)),(('a','b'),(float('nan'),.5))]:
            with self.assertRaises(ValueError): Decision(labels,p,'fixture')

    def test_action_enumeration(self):
        rng=np.random.default_rng(3)
        for _ in range(100):
            p=rng.random(); loss=rng.uniform(0,100,3); q=rng.random(3)
            cost=rng.random(3); friction=rng.random(3)
            index,values=choose_action(p,loss,q,cost,friction)
            oracle=[p*loss[j]*(1-q[j])+cost[j]+(1-p)*friction[j] for j in range(3)]
            self.assertTrue(np.allclose(values,oracle)); self.assertEqual(index,np.argmin(oracle))

    def test_invalid_actions(self):
        for p,q in [(float('nan'),[0]),(.5,[1.1])]:
            with self.assertRaises(ValueError): choose_action(p,[1],q,[1],[1])

    def test_threshold_abstention_and_perfect_sample(self):
        self.assertEqual(select_threshold([.9]*10,[1]*10)[0],0)
        n,t,u=select_threshold([.95]*4000,[1]*4000)
        self.assertEqual(n,4000); self.assertLessEqual(u,.1)
        self.assertLessEqual(t,.95)
        self.assertEqual(select_threshold([.99]*4000,[0]*4000)[0],0)

    def test_spans_and_tampering(self):
        source='Ingreso: 2.000.000 COP; café.'
        e=extract_literal(source,'2.000.000')
        self.assertTrue(e.verify(source)); self.assertFalse(e.verify(source+' '))
        self.assertFalse(Evidence(e.document_hash,e.start,e.end,'9').verify(source))
        self.assertFalse(Evidence(e.document_hash,True,e.end,e.value).verify(source))
        self.assertIsNone(extract_literal('x x','x'))
        self.assertIsNone(extract_literal(source,'ausente'))

    def test_schema_does_not_prove_truth(self):
        wrong=Decision(('fraude','legitimo'),(.99,.01),'synthetic-wrong')
        self.assertGreater(wrong.probabilities[0],.9)
        # A well-formed answer remains compatible with a legitimate case.
        self.assertEqual(sum(wrong.probabilities),1)


if __name__=='__main__': unittest.main()
