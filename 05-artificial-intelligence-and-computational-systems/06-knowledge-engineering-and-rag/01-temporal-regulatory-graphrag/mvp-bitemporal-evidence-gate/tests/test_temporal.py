import random
import unittest
from dataclasses import replace

from src.fixtures import fixture
from src.temporal import contains, digest, integrity_ok, select


class TemporalTests(unittest.TestCase):
    def test_all_fixture_outcomes(self):
        for seed in range(8):
            _, cases = fixture(seed)
            for c in cases:
                r = select(c["versions"], c["key"], c["valid_on"], c["known_on"])
                self.assertEqual(r.status, c["expected_status"])
                self.assertEqual(
                    r.citations[0].version.version_id if r.citations else None,
                    c["expected_version"],
                )

    def test_transaction_boundary_exclusive(self):
        versions, _ = fixture(0)
        r = select(versions, versions[0].key, "2026-01-15", "2026-03-01")
        self.assertEqual(r.citations[0].version.version_id, "s0-v2a")

    def test_valid_boundary_exclusive(self):
        versions, _ = fixture(0)
        r = select(versions, versions[0].key, "2026-02-01", "2026-04-01")
        self.assertEqual(r.citations[0].version.version_id, "s0-v2b")

    def test_future_evidence_negative_control(self):
        versions, _ = fixture(0)
        r = select(versions, versions[0].key, "2026-01-15", "2026-02-15", "valid_only")
        self.assertEqual(r.citations[0].version.version_id, "s0-v2a")

    def test_conflict_has_no_citation(self):
        _, cases = fixture(0)
        c = cases[-1]
        r = select(c["versions"], c["key"], c["valid_on"], c["known_on"])
        self.assertEqual(r.status, "ambiguous")
        self.assertEqual(r.citations, ())
        self.assertEqual(len(r.candidate_ids), 2)

    def test_input_order_invariance_property(self):
        rng = random.Random(42)
        versions, _ = fixture(0)
        expected = select(versions, versions[0].key, "2026-01-15", "2026-04-01")
        for _ in range(100):
            rng.shuffle(versions)
            self.assertEqual(
                select(versions, versions[0].key, "2026-01-15", "2026-04-01"), expected
            )

    def test_fingerprint_detects_changed_payload(self):
        versions, _ = fixture(0)
        r = select(versions, versions[0].key, "2026-01-15", "2026-04-01")
        citation = r.citations[0]
        self.assertTrue(integrity_ok(citation))
        self.assertFalse(
            integrity_ok(
                replace(citation, version=replace(citation.version, text="modified"))
            )
        )
        self.assertNotEqual(digest(versions[0]), digest(versions[1]))

    def test_invalid_intervals_dates_duplicates(self):
        versions, _ = fixture(0)
        v = versions[0]
        bad = [
            replace(v, known_to=v.known_from),
            replace(v, valid_to="2025-01-01"),
            replace(v, valid_from="20260101"),
            replace(v, text=""),
        ]
        for row in bad:
            with self.assertRaises(ValueError):
                select([row], v.key, "2026-01-15", "2026-04-01")
        with self.assertRaises(ValueError):
            select([v, v], v.key, "2026-01-15", "2026-04-01")

    def test_unknown_key_and_modes(self):
        versions, _ = fixture(0)
        self.assertEqual(
            select(versions, "unknown", "2026-01-15", "2026-04-01").status, "not_found"
        )
        with self.assertRaises(ValueError):
            select(versions, "x", "2026-01-15", "2026-04-01", "bad")
        self.assertTrue(contains("2026-01-01", None, "2027-01-01"))


if __name__ == "__main__":
    unittest.main()
