import unittest
from src.delta_replay import Delta, replay


class ReplayTests(unittest.TestCase):
    def test_late_unlink_retroactive_correction_respects_cutoff(self):
        ev = [
            Delta("a|b", "link", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z", "1"),
            Delta("a|b", "unlink", "2026-01-02T00:00:00Z", "2026-01-04T00:00:00Z", "2"),
        ]
        self.assertEqual(
            replay(
                ev, identity_at="2026-01-03T00:00:00Z", cutoff="2026-01-03T00:00:00Z"
            ),
            {"a|b"},
        )
        self.assertEqual(
            replay(
                ev, identity_at="2026-01-03T00:00:00Z", cutoff="2026-01-05T00:00:00Z"
            ),
            set(),
        )

    def test_event_order_irrelevant(self):
        ev = [
            Delta("e", "link", "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z", "a"),
            Delta("e", "unlink", "2026-01-03T00:00:00Z", "2026-01-04T00:00:00Z", "b"),
        ]
        args = dict(identity_at="2026-01-05T00:00:00Z", cutoff="2026-01-05T00:00:00Z")
        self.assertEqual(replay(ev, **args), replay(ev[::-1], **args))

    def test_duplicate_and_conflict_block(self):
        e = Delta("e", "link", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z", "x")
        with self.assertRaises(ValueError):
            replay([e, e], identity_at=e.effective_at, cutoff=e.available_at)
        x = Delta("e", "unlink", e.effective_at, e.available_at, "y")
        with self.assertRaises(ValueError):
            replay([e, x], identity_at=e.effective_at, cutoff=e.available_at)

    def test_cutoff_invariance_for_future_duplicate_or_malformed_payload(self):
        event = Delta("e", "link", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z", "x")
        future = Delta("e", "not-an-action", "not-a-date", "2026-02-01T00:00:00Z", "x")  # type: ignore[arg-type]
        args = dict(identity_at="2026-01-02T00:00:00Z", cutoff="2026-01-10T00:00:00Z")
        self.assertEqual(replay([event], **args), replay([event, future], **args))

    def test_superseded_conflicting_tie_does_not_block(self):
        events = [
            Delta("e", "link", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z", "a"),
            Delta("e", "link", "2026-01-02T00:00:00Z", "2026-01-02T00:00:00Z", "b"),
            Delta("e", "unlink", "2026-01-02T00:00:00Z", "2026-01-02T00:00:00Z", "c"),
            Delta("e", "unlink", "2026-01-03T00:00:00Z", "2026-01-03T00:00:00Z", "d"),
        ]
        args = dict(identity_at="2026-01-04T00:00:00Z", cutoff="2026-01-04T00:00:00Z")
        self.assertEqual(replay(events, **args), set())
        self.assertEqual(replay(events[::-1], **args), set())

    def test_conflict_at_final_maximum_blocks_in_any_order(self):
        events = [
            Delta("e", "link", "2026-01-02T00:00:00Z", "2026-01-02T00:00:00Z", "a"),
            Delta("e", "unlink", "2026-01-02T00:00:00Z", "2026-01-02T00:00:00Z", "b"),
        ]
        args = dict(identity_at="2026-01-03T00:00:00Z", cutoff="2026-01-03T00:00:00Z")
        for ordered in (events, events[::-1]):
            with self.assertRaisesRegex(ValueError, "conflicting effective-time tie"):
                replay(ordered, **args)

    def test_timezone_naive_rejected(self):
        with self.assertRaises(ValueError):
            replay([], identity_at="2026-01-01T00:00:00", cutoff="2026-01-01T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
