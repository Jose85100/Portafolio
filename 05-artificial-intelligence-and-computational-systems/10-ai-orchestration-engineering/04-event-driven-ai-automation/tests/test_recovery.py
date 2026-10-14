import tempfile
from pathlib import Path
import unittest
from src.engine import Event, Inbox
from src.experiment import make_workload, run

class TestRecovery(unittest.TestCase):
    def test_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"state.db"
            with Inbox(path) as engine:
                engine.receive(Event("a", 4), {"a"})
            with Inbox(path) as engine:
                engine.drain()
                self.assertEqual(engine.totals(), (1, 4))
    def test_no_retry_ablation(self):
        result=run(make_workload(0, n=50, fault_rate=1), "inbox_no_retry")
        self.assertGreater(result["pending"], 0)
    def test_baseline_replay(self):
        result=run(make_workload(4, n=40, duplicate_rate=0.5), "naive")
        self.assertGreater(result["replay_delta"], 0)
    def test_invalid_message(self):
        with Inbox() as engine:
            self.assertEqual(engine.receive(Event("a", -2)), "invalid")
    def test_deterministic_workload(self):
        self.assertEqual(make_workload(15), make_workload(15))
