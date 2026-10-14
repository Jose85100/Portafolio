import unittest
from src.engine import Event, Inbox, valid
from src.experiment import make_workload, run

class TestProperties(unittest.TestCase):
    def test_schema(self):
        self.assertTrue(valid(Event("ok", 0)))
        self.assertFalse(valid(Event("bad", -1)))
    def test_conflict(self):
        with Inbox() as engine:
            engine.receive(Event("a", 5))
            self.assertEqual(engine.receive(Event("a", 8)), "conflict")
    def test_recovery(self):
        with Inbox() as engine:
            engine.receive(Event("a", 10), {"a"})
            self.assertEqual(engine.totals(), (0, 0))
            engine.drain()
            self.assertEqual(engine.totals(), (1, 10))
    def test_randomized(self):
        for seed in range(20):
            result=run(make_workload(seed, n=35), "inbox")
            self.assertEqual(result["absolute_error"], 0)
            self.assertEqual(result["replay_delta"], 0)
