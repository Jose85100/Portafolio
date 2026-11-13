import unittest
from src.engine import Event, Inbox

class TestInbox(unittest.TestCase):
    def test_duplicate(self):
        with Inbox() as engine:
            engine.receive(Event('a', 4))
            self.assertEqual(engine.receive(Event('a', 4)), 'duplicate')
