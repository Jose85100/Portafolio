import itertools
import math
import unittest
import numpy as np
from src.engine import Case,Action,Scenario,expected_cost,optimize,shared_entity_count
from src.models import Models,generate

ALLOW=Action('allow',0,0,0,0)
VERIFY=Action('verify',.35,4000,2500,3)
REVIEW=Action('review',.8,18000,15000,15)


def enumeration(cases,actions,capacity,scenarios,weights,kind):
    """Independent small-case oracle: no calls to expected_cost or MILP."""
    best=math.inf
    for choices in itertools.product(range(len(actions)),repeat=len(cases)):
        if sum(actions[a].effort_minutes for a in choices)>capacity:continue
        totals=[]
        for s in scenarios:
            total=0.
            for case,a in zip(cases,choices):
                action=actions[a];p=min(case.probability*s.probability_multiplier,1)
                q=min(action.prevent_fraction*s.effectiveness_multiplier,1)
                total+=p*case.loss_cop*s.severity_multiplier*(1-q)+action.cost_cop+(1-p)*action.legitimate_friction_cop
            totals.append(total)
        objective=max(totals) if kind=='worst_case' else sum(w*c for w,c in zip(weights,totals))
        best=min(best,objective)
    return best


class LossContracts(unittest.TestCase):
    def test_invalid_probability(self):
        for p in (-.1,1.1,math.nan,math.inf,True,'0.1'):
            with self.subTest(p=p),self.assertRaises(ValueError):Case('x',p,100)

    def test_invalid_loss(self):
        for loss in (-1,math.inf,math.nan):
            with self.assertRaises(ValueError):Case('x',.1,loss)

    def test_invalid_action(self):
        for args in [('x',1.1,0,0,0),('x',.5,-1,0,0),('x',.5,0,0,-1),('',0,0,0,0)]:
            with self.assertRaises(ValueError):Action(*args)

    def test_invalid_scenario(self):
        with self.assertRaises(ValueError):Scenario('x',effectiveness_multiplier=-1)

    def test_cost_by_outcomes(self):
        # Enumerate Bernoulli fraud and prevention; legitimate friction only on Y=0.
        p,L,q=.23,900_000,.6
        a=Action('review',q,10000,3000,10)
        oracle=p*q*10000+p*(1-q)*(L+10000)+(1-p)*(10000+3000)
        self.assertAlmostEqual(expected_cost(Case('x',p,L),a),oracle)

    def test_no_prevention_costs_more(self):
        c=Case('x',.8,1_000_000);s=Scenario('zero',effectiveness_multiplier=0)
        self.assertGreater(expected_cost(c,REVIEW,s),expected_cost(c,ALLOW,s))

    def test_overflow_rejected(self):
        with self.assertRaises(ValueError):expected_cost(Case('x',1,1e308),ALLOW,Scenario('huge',severity_multiplier=1e308))


class Optimization(unittest.TestCase):
    def test_bruteforce_random_finite_scenarios(self):
        rng=np.random.default_rng(31);actions=[ALLOW,VERIFY,REVIEW]
        scenarios=[Scenario('base'),Scenario('stress',1.4,1.7,.6),Scenario('low',.6,.8,1.1)]
        for iteration in range(20):
            cases=[Case(str(i),float(rng.uniform(.01,.8)),float(rng.uniform(1e4,2e6))) for i in range(4)]
            capacity=int(rng.integers(0,40))
            for kind in ('expected','worst_case'):
                with self.subTest(iteration=iteration,kind=kind):
                    plan=optimize(cases,actions,capacity,scenarios,[.6,.3,.1],kind)
                    oracle=enumeration(cases,actions,capacity,scenarios,[.6,.3,.1],kind)
                    self.assertAlmostEqual(plan['objective_cop'],oracle,places=5)
                    self.assertLessEqual(plan['effort_minutes'],capacity+1e-7)

    def test_probability_rank_counterexample(self):
        # Same review effectiveness/cost. Lower fraud probability, much larger loss.
        cases=[Case('high_p',.9,100_000),Case('large_loss',.2,2_000_000)]
        result=optimize(cases,[ALLOW,REVIEW],15)
        self.assertEqual(result['actions'],['allow','review'])

    def test_zero_capacity(self):
        self.assertEqual(optimize([Case('x',.9,1e6)],[ALLOW,REVIEW],0)['actions'],['allow'])

    def test_uneconomic_review(self):
        self.assertEqual(optimize([Case('x',.001,100)],[ALLOW,VERIFY,REVIEW],100)['actions'],['allow'])

    def test_capacity_monotonic(self):
        cases=[Case('a',.2,1e6),Case('b',.1,2e6)]
        values=[optimize(cases,[ALLOW,VERIFY,REVIEW],c)['objective_cop'] for c in (0,3,15,30)]
        self.assertTrue(all(a>=b-1e-6 for a,b in zip(values,values[1:])))

    def test_deduplication_required(self):
        with self.assertRaises(ValueError):optimize([Case('x',.1,1),Case('x',.2,1)],[ALLOW],0)

    def test_scenario_weights(self):
        for w in ([-1,2],[.2,.2],[1],[math.nan,1]):
            with self.assertRaises(ValueError):optimize([Case('x',.1,1)],[ALLOW],0,[Scenario('a'),Scenario('b')],w)

    def test_malformed_optimization(self):
        c=[Case('x',.1,1)]
        for kw in (dict(cases=[]),dict(actions=[]),dict(scenarios=[]),dict(objective='CVaR'),dict(capacity_minutes=-1)):
            args=dict(cases=c,actions=[ALLOW],capacity_minutes=0);args.update(kw)
            with self.assertRaises(ValueError):optimize(**args)

    def test_allow_action_required(self):
        with self.assertRaises(ValueError):optimize([Case('x',.1,1)],[REVIEW],20)

    def test_duplicate_actions_or_scenarios(self):
        with self.assertRaises(ValueError):optimize([Case('x',.1,1)],[ALLOW,ALLOW],0)
        with self.assertRaises(ValueError):optimize([Case('x',.1,1)],[ALLOW],0,[Scenario('a'),Scenario('a')])


class Temporal(unittest.TestCase):
    def test_future_and_delayed_evidence(self):
        links=[dict(application_id='old',entity='device',event_at=5.,available_at=5.),
               dict(application_id='late',entity='device',event_at=6.,available_at=15.),
               dict(application_id='current',entity='device',event_at=9.,available_at=9.)]
        count=shared_entity_count(links,'device',10.,'current')
        future=dict(application_id='future',entity='device',event_at=12.,available_at=12.)
        self.assertEqual(count,1)
        self.assertEqual(shared_entity_count(links+[future],'device',10.,'current'),count)
        self.assertEqual(shared_entity_count(links,'device',16.,'current'),2)

    def test_duplicates_and_boundary(self):
        link=dict(application_id='a',entity='d',event_at=5.,available_at=5.)
        self.assertEqual(shared_entity_count([link,link],'d',10.,window=5.),1)
        self.assertEqual(shared_entity_count([link],'d',5.),0)
        self.assertEqual(shared_entity_count([link],'d',11.,window=5.),0)

    def test_chronological_labels(self):
        d=generate();m=Models().fit(d)
        self.assertFalse((m.train&m.calibration).any());self.assertFalse((m.calibration&m.test).any())
        self.assertTrue((d['label_available'][m.train]<=80).all())
        self.assertTrue((d['label_available'][m.calibration]<=110).all())

    def test_future_data_cannot_change_fitted_model(self):
        d=generate();m=Models().fit(d);original=m.predict(d['x'][m.test])
        changed={k:v.copy() for k,v in d.items()}
        changed['x'][m.test]=1.;changed['y'][m.test]=1-d['y'][m.test]
        later=Models().fit(changed)
        for key,value in original.items():
            np.testing.assert_allclose(value,later.predict(d['x'][m.test])[key],rtol=0,atol=0)


if __name__=='__main__':unittest.main()
