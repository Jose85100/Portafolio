import os
import tempfile
import unittest
from pathlib import Path

from src.broker import Denied, ReadBroker, parse_request
from src.fixtures import CASES, setup


class BrokerTests(unittest.TestCase):
    def test_no_escape_in_all_fixtures(self):
        for case in CASES:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                root, payload, hook, safe, canary = setup(Path(tmp), case, 0)
                with ReadBroker(root) as broker:
                    try:
                        result = broker.read(payload, fault_hook=hook)
                    except Denied:
                        continue
                    self.assertEqual(result, safe)
                    self.assertNotEqual(result, canary)

    def test_resolve_race_negative_control(self):
        for case in ("race_parent", "race_leaf"):
            with tempfile.TemporaryDirectory() as tmp:
                root, payload, hook, _, canary = setup(Path(tmp), case, 1)
                with ReadBroker(root, "resolve_then_open") as broker:
                    self.assertEqual(broker.read(payload, fault_hook=hook), canary)

    def test_prefix_traversal_negative_control(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, payload, _, _, canary = setup(Path(tmp), "traversal", 2)
            with ReadBroker(root, "prefix") as broker:
                self.assertEqual(broker.read(payload), canary)

    def test_parent_descriptor_preserves_granted_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, payload, hook, safe, _ = setup(Path(tmp), "race_parent", 3)
            with ReadBroker(root) as broker:
                self.assertEqual(broker.read(payload, fault_hook=hook), safe)

    def test_internal_symlink_utility_tradeoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, payload, _, safe, _ = setup(Path(tmp), "internal_alias", 4)
            with ReadBroker(root, "resolve_then_open") as broker:
                self.assertEqual(broker.read(payload), safe)
            with ReadBroker(root) as broker, self.assertRaises(Denied):
                broker.read(payload)

    def test_schema_fails_closed(self):
        for payload in [
            None,
            {},
            {"tool": "read_text", "path": "x", "max_bytes": True},
            {"tool": "read_text", "path": "x", "max_bytes": 1, "approval": True},
            {"tool": "write", "path": "x", "max_bytes": 1},
        ]:
            with self.assertRaises(Denied):
                parse_request(payload)

    def test_oversized_and_binary_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "big").write_bytes(b"x" * 50)
            (root / "binary").write_bytes(b"\xff")
            with ReadBroker(root) as broker:
                for path, limit in [("big", 10), ("binary", 10)]:
                    with self.assertRaises(Denied):
                        broker.read(
                            {"tool": "read_text", "path": path, "max_bytes": limit}
                        )

    def test_fifo_nonblocking_denial(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            os.mkfifo(root / "pipe")
            with ReadBroker(root) as broker, self.assertRaises(Denied):
                broker.read({"tool": "read_text", "path": "pipe", "max_bytes": 10})

    def test_no_descriptor_leak_on_denials(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _, _, _, _ = setup(Path(tmp), "safe", 5)
            with ReadBroker(root) as broker:
                before = len(list(Path("/proc/self/fd").iterdir()))
                for _ in range(100):
                    with self.assertRaises(Denied):
                        broker.read(
                            {
                                "tool": "read_text",
                                "path": "nested/missing",
                                "max_bytes": 10,
                            }
                        )
                self.assertEqual(len(list(Path("/proc/self/fd").iterdir())), before)

    def test_closed_broker_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, req, _, _, _ = setup(Path(tmp), "safe", 6)
            broker = ReadBroker(root)
            broker.close()
            broker.close()
            with self.assertRaises(Denied):
                broker.read(req)


if __name__ == "__main__":
    unittest.main()
