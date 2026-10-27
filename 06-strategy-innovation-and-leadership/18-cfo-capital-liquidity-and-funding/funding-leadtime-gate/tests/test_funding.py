import unittest
from dataclasses import replace
from src.funding import Facility, choose, score, simulate


class FundingTests(unittest.TestCase):
    def test_identity_and_principal_not_income(self):
        for lead in (0,1,2):
            result=simulate([-1,-2,1,-3,2],8,replace(Facility(),lead=lead))
            self.assertLess(result['reconciliation_error'],1e-10)
            self.assertAlmostEqual(result['cash'][-1]-result['debt'][-1],8-3-result['costs'])

    def test_observation_nonanticipativity(self):
        # Future paths differ: identical current information must request alike.
        a=simulate([-2,-2,0,0,0],6,Facility())
        b=simulate([-2,99,99,99,99],6,Facility())
        self.assertEqual(a['request_period'],1)
        self.assertEqual(a['request_period'],b['request_period'])

    def test_lead_late_and_zero(self):
        flows=[-2]*5
        self.assertIsNotNone(simulate(flows,2,Facility())['first_breach'])
        self.assertIsNone(simulate(flows,6,Facility())['first_breach'])
        immediate=simulate(flows,2,replace(Facility(),lead=0))
        self.assertEqual(immediate['request_period'],immediate['funding_period'])
        self.assertIsNone(immediate['first_breach'])

    def test_monitor_start_and_fee(self):
        self.assertEqual(simulate([1,1,1],None,replace(Facility(),initial_cash=0,floor=1))['first_breach'],-1)
        self.assertEqual(simulate([1,1,1],0,replace(Facility(),initial_cash=0))['first_breach'],0)
        self.assertIsNone(simulate([1,1,1],None,Facility())['request_period'])
        self.assertIsNone(simulate([0],8,Facility())['request_period'])

    def test_fixed_request_closed_form_oracle(self):
        path=[-1,-2,1,-3,2]
        result=simulate(path,8,Facility())
        prefix=0
        for t,flow in enumerate(path):
            prefix+=flow
            drawn=8 if t>=2 else 0
            interest=.16*max(0,t-1)
            self.assertAlmostEqual(result['cash'][t],8-.5+prefix+drawn-interest)
            self.assertEqual(result['debt'][t],drawn)

    def test_policy_and_invalid(self):
        paths=[[-1,-1,1,1,1],[-2,-2,-2,-2,-2],[-4,-2,-1,-1,-1]]
        selected=choose(paths,[.5,.3,.2],[None,0,2,4,6,8],Facility(),.1)
        self.assertEqual(selected['threshold'],6)
        self.assertEqual(selected['breach_probability'],0)
        self.assertAlmostEqual(selected['expected_cost'],.74)
        with self.assertRaises(ValueError):
            choose([[-20]*5],[1],[None,0],Facility(),0)
        for args in (([],[],None),([[1],[1,2]],[.5,.5],None),([[1]],[.5],None)):
            with self.assertRaises(ValueError):
                score(*args,Facility())
        for flows,h in (([],0),([float('nan')],0),([1],float('nan'))):
            with self.assertRaises(ValueError):
                simulate(flows,h,Facility())
        for kwargs in ({'lead':-1},{'lead':True},{'amount':-1},{'floor':float('nan')}):
            with self.assertRaises(ValueError):
                Facility(**kwargs)
        with self.assertRaises(ValueError):
            choose(paths,[.5,.3,.2],[],Facility(),.1)
