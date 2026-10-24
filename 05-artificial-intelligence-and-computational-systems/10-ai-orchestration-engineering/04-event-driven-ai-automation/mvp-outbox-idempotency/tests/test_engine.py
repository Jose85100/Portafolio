import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.engine import (
    LostAcknowledgement,
    PayloadConflict,
    apply,
    dispatch,
    enqueue,
    initialize,
    metrics,
)


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.sender = Path(self.temp.name) / "sender.sqlite"
        self.provider = Path(self.temp.name) / "provider.sqlite"
        initialize(self.sender, self.provider)

    def tearDown(self):
        self.temp.cleanup()

    def test_outbox_enqueue_idempotent_and_conflict(self):
        enqueue(self.sender, "tenant/a", 10)
        enqueue(self.sender, "tenant/a", 10)
        with self.assertRaises(PayloadConflict):
            enqueue(self.sender, "tenant/a", 11)
        self.assertEqual(metrics(self.sender, self.provider)["jobs"], 1)

    def test_hard_process_crash_commit_recovered(self):
        enqueue(self.sender, "tenant/a", 10)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.worker",
                str(self.sender),
                str(self.provider),
                "tenant/a",
                "key_hash",
            ],
            check=False,
        )
        self.assertEqual(result.returncode, 77)
        self.assertEqual(metrics(self.sender, self.provider)["acknowledged"], 0)
        self.assertEqual(metrics(self.sender, self.provider)["effects"], 1)
        dispatch(self.sender, self.provider, "tenant/a", "key_hash")
        self.assertEqual(metrics(self.sender, self.provider)["duplicates"], 0)
        self.assertEqual(metrics(self.sender, self.provider)["acknowledged"], 1)

    def test_no_dedup_negative_control(self):
        enqueue(self.sender, "tenant/a", 10)
        with self.assertRaises(LostAcknowledgement):
            dispatch(self.sender, self.provider, "tenant/a", "no_dedup", True)
        dispatch(self.sender, self.provider, "tenant/a", "no_dedup")
        self.assertEqual(metrics(self.sender, self.provider)["duplicates"], 1)

    def test_semantic_conflict_rejected_and_not_applied(self):
        apply(self.provider, "tenant/a", 10, "key_hash")
        with self.assertRaises(PayloadConflict):
            apply(self.provider, "tenant/a", 11, "key_hash")
        self.assertEqual(metrics(self.sender, self.provider)["effects"], 1)

    def test_key_only_negative_control(self):
        first = apply(self.provider, "tenant/a", 10, "key_only")
        self.assertEqual(first, apply(self.provider, "tenant/a", 11, "key_only"))

    def test_randomized_retry_invariant(self):
        rng = random.Random(42)
        for i in range(25):
            key = f"tenant/{i}"
            enqueue(self.sender, key, i + 1)
            for _ in range(rng.randrange(8)):
                with self.assertRaises(LostAcknowledgement):
                    dispatch(self.sender, self.provider, key, "key_hash", True)
            dispatch(self.sender, self.provider, key, "key_hash")
        result = metrics(self.sender, self.provider)
        self.assertEqual(result["effects"], 25)
        self.assertEqual(result["duplicates"], 0)
        self.assertEqual(result["acknowledged"], 25)

    def test_already_ack_does_not_redeliver(self):
        enqueue(self.sender, "tenant/a", 10)
        self.assertTrue(dispatch(self.sender, self.provider, "tenant/a", "key_hash"))
        self.assertFalse(dispatch(self.sender, self.provider, "tenant/a", "key_hash"))

    def test_concurrent_provider_retry_serialized(self):
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=4) as pool:
            receipts = list(
                pool.map(
                    lambda _: apply(self.provider, "tenant/concurrent", 7, "key_hash"),
                    range(12),
                )
            )
        self.assertEqual(len(set(receipts)), 1)
        self.assertEqual(metrics(self.sender, self.provider)["effects"], 1)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            initialize(self.sender, self.sender)
        with self.assertRaises(ValueError):
            enqueue(self.sender, "", 1)
        with self.assertRaises(ValueError):
            enqueue(self.sender, "tenant/a", True)
        with self.assertRaises(ValueError):
            apply(self.provider, "tenant/a", 0, "key_hash")
        with self.assertRaises(ValueError):
            apply(self.provider, "tenant/a", 1, "invalid")
        with self.assertRaises(KeyError):
            dispatch(self.sender, self.provider, "missing", "key_hash")


if __name__ == "__main__":
    unittest.main()
