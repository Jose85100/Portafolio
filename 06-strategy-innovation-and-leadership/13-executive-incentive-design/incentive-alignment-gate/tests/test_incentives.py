import unittest
from dataclasses import replace
from src.incentives import Action,audit,design,evaluate,response


def sample():
    return [Action('prudent',100,.05,20,-10,1),Action('volume_chasing',150,.5,35,-50,0)]


class IncentiveTests(unittest.TestCase):
    def test_two_action_analytic_boundary(self):
        actions=sample()
        boundary=(15-10+1+.05)/(15*.5-10*.05)
        self.assertAlmostEqual(boundary,6.05/7)
        self.assertAlmostEqual(audit(actions,'prudent',.1,boundary)['ic_margin'],.05)
        with self.assertRaises(ValueError):
            design(actions,'prudent',.1,[0,.8])
        self.assertEqual(design(actions,'prudent',.1,[0,.9,1])['deferred'],.9)

    def test_limited_liability_and_transfer_identity(self):
        for action in sample():
            for f in (0,.5,1):
                row=evaluate(action,.1,f)
                self.assertGreaterEqual(row['failure_bonus'],0)
                self.assertLessEqual(row['failure_bonus'],row['success_bonus'])
                self.assertAlmostEqual(row['net_profit']+row['expected_bonus'],row['gross_profit'])
                weighted=(1-action.failure_probability)*row['success_bonus']+action.failure_probability*row['failure_bonus']
                self.assertAlmostEqual(weighted,row['expected_bonus'])

    def test_response_participation_and_adverse_ties(self):
        self.assertEqual(response(sample(),.1,0)['name'],'volume_chasing')
        self.assertEqual(response(sample(),.1,.9)['name'],'prudent')
        self.assertEqual(response(sample(),.1,.9,100)['name'],'OUTSIDE')
        tied=[Action('good',10,.5,10,10,0),Action('bad',10,.5,-10,-10,0)]
        self.assertEqual(response(tied,.1,0)['name'],'bad')
        with self.assertRaises(ValueError):
            design(sample(),'prudent',.1,[.9,1],outside=100)

    def test_omitted_action_counterexample(self):
        extra=Action('unmodeled',300,.01,0,-100,0)
        self.assertNotEqual(response(sample()+[extra],.1,.9)['name'],'prudent')
        with self.assertRaises(ValueError):
            design(sample()+[extra],'prudent',.1,[0,.9,1])

    def test_invalid_and_single_action(self):
        with self.assertRaises(ValueError):
            Action('bad',1,2,1,0,0)
        with self.assertRaises(ValueError):
            Action('OUTSIDE',1,.5,1,0,0)
        for rate,f in ((-.1,0),(.1,-1),(.1,float('nan'))):
            with self.assertRaises(ValueError):
                evaluate(sample()[0],rate,f)
        with self.assertRaises(ValueError):
            response([],0,0)
        with self.assertRaises(ValueError):
            audit(sample(),'absent',.1,0)
        with self.assertRaises(ValueError):
            design(sample(),'prudent',.1,[],0)
        solo=[replace(sample()[0],effort_cost=0)]
        self.assertGreater(audit(solo,'prudent',.1,.9)['ic_margin'],0)
