import unittest
from src.engine import Event, Inbox
from src.experiment import make_workload

class TestContracts(unittest.TestCase):
    def test_unknown(self):
        with Inbox() as engine:
            with self.assertRaises(KeyError):
                engine.attempt("missing")
    def test_empty(self):
        with Inbox() as engine:
            self.assertEqual(engine.totals(), (0, 0))
            self.assertEqual(engine.drain(), 0)
    def test_invalid_config(self):
        with self.assertRaises(ValueError):
            make_workload(0, n=0)
