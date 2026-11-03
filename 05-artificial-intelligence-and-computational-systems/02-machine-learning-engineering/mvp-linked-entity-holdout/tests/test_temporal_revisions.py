from dataclasses import replace
import unittest

from src.temporal_revisions import Revision, filter_validity_first, select_full_replacements


class TemporalRevisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.history = [
            Revision("x", "r0", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z", None, "old"),
            Revision("x", "r1", "2026-01-03T00:00:00Z", "2026-01-05T00:00:00Z", "2026-01-09T00:00:00Z", "new"),
        ]

    def test_select_latest_then_interval_does_not_revive_expired_open_revision(self) -> None:
        good = select_full_replacements(self.history, as_of="2026-01-04T00:00:00Z", identity_at="2026-01-02T00:00:00Z")
        wrong = filter_validity_first(self.history, as_of="2026-01-04T00:00:00Z", identity_at="2026-01-02T00:00:00Z")
        self.assertEqual((good[0].revision_id, good[0].status), ("r1", "not-effective-at-identity-time"))
        self.assertEqual((wrong[0].revision_id, wrong[0].status), ("r0", "eligible"))

    def test_future_available_revision_is_invisible_at_cutoff(self) -> None:
        selected = select_full_replacements(self.history, as_of="2026-01-02T23:59:59Z", identity_at="2026-01-06T00:00:00Z")
        self.assertEqual(selected[0].revision_id, "r0")

    def test_half_open_interval(self) -> None:
        at_end = select_full_replacements(self.history, as_of="2026-01-04T00:00:00Z", identity_at="2026-01-09T00:00:00Z")
        self.assertEqual(at_end[0].status, "not-effective-at-identity-time")

    def test_latest_revision_can_be_future_effective_and_does_not_fallback(self) -> None:
        selected = select_full_replacements(self.history, as_of="2026-01-04T00:00:00Z", identity_at="2026-01-04T00:00:00Z")
        self.assertEqual(selected[0].revision_id, "r1")
        self.assertNotEqual(selected[0].status, "eligible")

    def test_utc_offsets_compare_as_instants(self) -> None:
        selected = select_full_replacements(self.history, as_of="2026-01-03T01:00:00+01:00", identity_at="2026-01-04T19:00:00-05:00")
        self.assertEqual(selected[0].revision_id, "r1")

    def test_naive_timestamp_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            select_full_replacements(self.history, as_of="2026-01-04T00:00:00", identity_at="2026-01-04T00:00:00Z")

    def test_invalid_interval_rejected(self) -> None:
        invalid = [replace(self.history[0], valid_until="2025-12-31T00:00:00Z")]
        with self.assertRaisesRegex(ValueError, "later than"):
            select_full_replacements(invalid, as_of="2026-01-04T00:00:00Z", identity_at="2026-01-04T00:00:00Z")

    def test_duplicate_revision_id_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unique"):
            select_full_replacements(self.history + [self.history[0]], as_of="2026-01-04T00:00:00Z", identity_at="2026-01-04T00:00:00Z")

    def test_tie_at_latest_availability_rejected(self) -> None:
        tied = self.history + [replace(self.history[1], revision_id="r1b", value="ambiguous")]
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            select_full_replacements(tied, as_of="2026-01-04T00:00:00Z", identity_at="2026-01-06T00:00:00Z")

    def test_multiple_identities_sorted(self) -> None:
        two = self.history + [Revision("a", "r0", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z", None, "a")]
        selected = select_full_replacements(two, as_of="2026-01-04T00:00:00Z", identity_at="2026-01-06T00:00:00Z")
        self.assertEqual([s.identity for s in selected], ["a", "x"])


if __name__ == "__main__":
    unittest.main()
