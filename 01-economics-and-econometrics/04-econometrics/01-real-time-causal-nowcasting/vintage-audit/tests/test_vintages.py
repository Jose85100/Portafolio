import sys
import unittest
from dataclasses import replace
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.vintages import Config, Release, evaluate, forecast, simulate, snapshot

class VintageTests(unittest.TestCase):
    def test_future_mutation_invariant(self):
        for seed in range(20):
            rows, _ = simulate(Config(seed=seed))
            for origin in (60, 100, 180):
                altered = [replace(r, value=r.value+10000) if r.available>origin else r for r in rows]
                self.assertEqual(forecast(rows, origin), forecast(altered, origin))
    def test_no_violations(self):
        for seed in range(10):
            rows, _ = simulate(Config(seed=seed))
            self.assertTrue(all(r.available<=80 for r in snapshot(rows,80).values()))
            self.assertEqual(forecast(rows,80)[1],0)
    def test_no_revision_no_delay_equal(self):
        rows, _ = simulate(Config(delay=0, revision=0))
        for origin in range(60,90):
            self.assertAlmostEqual(forecast(rows,origin)[0],forecast(rows,origin,True,True)[0])
    def test_duplicate_release_latest(self):
        rows=[Release("x",0,1,1.,False),Release("x",0,4,2.,True)]
        self.assertEqual(snapshot(rows,2)[("x",0)].value,1.)
        self.assertEqual(snapshot(rows,4)[("x",0)].value,2.)
        self.assertEqual(snapshot(rows,0),{})
    def test_reproducible(self):
        a, y=simulate(Config(seed=7)); b,z=simulate(Config(seed=7))
        self.assertEqual(a,b); np.testing.assert_array_equal(y,z)
    def test_invalid_config(self):
        for kwargs in ({"n":10},{"delay":-1},{"revision":-1},{"rho":1},{"revision":float("nan")},{"revision":float("inf")}):
            with self.assertRaises(ValueError): Config(**kwargs)
    def test_long_delay_excludes_unreleased_training(self):
        rows,_=simulate(Config(delay=10))
        self.assertEqual(forecast(rows,80)[1],0)
    def test_small_history(self):
        with self.assertRaises(ValueError): forecast([],10)
    def test_baseline_agrees_numpy(self):
        from src.vintages import core
        x=[1.,2.,3.,4.]; y=[2.,4.,5.,8.]
        a,b=core.ols(x,y)
        expected=np.linalg.lstsq(np.column_stack([np.ones(4),x]),y,rcond=None)[0]
        np.testing.assert_allclose([a,b],expected,atol=1e-12)
    def test_positive_control_detected(self):
        r=evaluate(Config())
        self.assertGreater(sum(x["violations"] for x in r if x["arm"]=="final_no_delay"),0)
        self.assertEqual(sum(x["violations"] for x in r if x["arm"]=="asof_ols"),0)

if __name__ == "__main__": unittest.main()
