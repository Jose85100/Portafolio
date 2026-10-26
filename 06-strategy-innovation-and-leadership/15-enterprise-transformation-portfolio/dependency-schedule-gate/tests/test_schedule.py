import unittest
from src.schedule import Job, exact, feasible, greedy, validate, value


class SchedulingTests(unittest.TestCase):
    def test_completion_before_start(self):
        jobs=[Job('a',1,0,2,1),Job('b',1,8,1,1,('a',))]
        self.assertFalse(feasible(jobs,{'a':0,'b':1},[4]*3,2))
        self.assertTrue(feasible(jobs,{'a':0,'b':2},[4]*3,2))
        self.assertFalse(feasible(jobs,{'b':0},[4]*3,2))

    def test_capacity_budget_dates(self):
        jobs=[Job('a',3,10,1,2)]
        for starts,budgets,people in [({'a':0},[2],2),({'a':0},[3],1),({'a':-1},[3],2),({'a':1},[3],2),({'unknown':0},[3],2)]:
            self.assertFalse(feasible(jobs,starts,budgets,people))

    def test_analytic_one_job(self):
        jobs=[Job('a',3,10,1,1)]
        result=exact(jobs,[3,3],1,.1)
        self.assertEqual(result['starts'],{'a':0})
        self.assertAlmostEqual(result['npv'],10/1.1-3)
        self.assertEqual(exact([Job('bad',3,1,1,1)],[3],1,0)['starts'],{})
        self.assertEqual(greedy([Job('bad',3,1,1,1)],[3],1,0)['starts'],{})

    def test_invariants(self):
        jobs=[Job('a',2,6,1,1),Job('b',2,8,1,1,('a',))]
        previous=0
        for capacity in (0,1,2):
            answer=exact(jobs,[4]*3,capacity,.1)
            self.assertTrue(feasible(jobs,answer['starts'],[4]*3,capacity))
            self.assertGreaterEqual(answer['npv'],previous-1e-10)
            self.assertGreaterEqual(answer['npv'],greedy(jobs,[4]*3,capacity,.1)['npv']-1e-10)
            previous=answer['npv']
        self.assertEqual(value(jobs,{},.1),0)

    def test_milp_oracle(self):
        import numpy as np
        from scipy.optimize import milp, Bounds, LinearConstraint
        jobs=[Job('a',2,0,2,1),Job('b',2,10,1,1,('a',)),Job('c',3,7,1,2)]
        horizon, discount = 4, .1
        options=[(j,t) for j in jobs for t in range(horizon-j.duration+1)]
        objective=np.array([j.cost/(1+discount)**t-j.benefit/(1+discount)**(t+j.duration) for j,t in options])
        constraints=[]
        upper=[]
        for j in jobs:
            constraints.append([int(k.name==j.name) for k,t in options])
            upper.append(1)
        for period in range(horizon):
            constraints.append([k.cost if t==period else 0 for k,t in options])
            upper.append(4)
            constraints.append([k.people if t<=period<t+k.duration else 0 for k,t in options])
            upper.append(2)
        lookup={j.name:j for j in jobs}
        for child,t in options:
            for dep in child.dependencies:
                constraints.append([int(k.name==child.name and s==t)-int(k.name==dep and s+lookup[dep].duration<=t) for k,s in options])
                upper.append(0)
        answer=milp(objective, integrality=np.ones(len(options)), bounds=Bounds(0,1),
                    constraints=LinearConstraint(np.array(constraints), -np.inf, np.array(upper)))
        self.assertTrue(answer.success)
        self.assertAlmostEqual(exact(jobs,[4]*horizon,2,discount)['npv'], -answer.fun, places=8)

    def test_enumeration_guard(self):
        with self.assertRaises(ValueError):
            exact([Job(str(i),1,2,1,1) for i in range(8)], [8]*20, 8, .1)

    def test_invalid(self):
        for jobs in ([Job('a',1,2,1,1),Job('a',1,2,1,1)], [Job('a',1,2,1,1,('bad',))], [Job('a',1,2,1,1,('b',)),Job('b',1,2,1,1,('a',))], [Job('a',1,2,0,1)]):
            with self.assertRaises(ValueError):
                validate(jobs,[4],1,.1)
        for budgets,capacity,discount in (([],1,.1),([1],-1,.1),([1],1,-.1),([float('nan')],1,.1)):
            with self.assertRaises(ValueError):
                validate([Job('a',1,2,1,1)],budgets,capacity,discount)
