from dataclasses import replace
import unittest
from src.partial_audit import partial_audit
from src.snapshot_gate import (
    AdjudicationSnapshot,
    prospective_audit,
    utc,
    verify_manifest,
)
from src.splitter import Record


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.rows = [Record("a", ("a",)), Record("b", ("b",))]
        self.assignment = {"a": "train", "b": "test"}
        self.cutoff = "2026-11-02T12:00:00+00:00"
        self.snapshot = AdjudicationSnapshot(
            tuple(self.rows),
            "synthetic-reviewer",
            1,
            "complete-equivalence-on-subset",
            self.cutoff,
            self.cutoff,
        )

    def test_boundary_and_original_exact(self):
        result = prospective_audit(
            self.rows, self.assignment, self.snapshot, self.cutoff
        )
        self.assertEqual(
            result.audit, partial_audit(self.rows, self.rows, self.assignment)
        )
        self.assertEqual(result.status, "metadata-eligible")

    def test_late_availability_not_event_time(self):
        result = prospective_audit(
            self.rows,
            self.assignment,
            replace(self.snapshot, available_at="2026-11-02T12:00:00.000001Z"),
            self.cutoff,
        )
        self.assertEqual(result.reasons, ("unavailable-at-cutoff",))
        self.assertIsNone(result.audit)

    def test_future_effective(self):
        r = prospective_audit(
            self.rows,
            self.assignment,
            replace(self.snapshot, effective_at="2026-11-03T00:00:00Z"),
            self.cutoff,
        )
        self.assertEqual(r.reasons, ("future-effective",))

    def test_semantics_source_version_abstain(self):
        for snap, reason in [
            (
                replace(self.snapshot, semantics="positive-links-only"),
                "insufficient-semantics",
            ),
            (replace(self.snapshot, source_id=" "), "missing-source"),
            (replace(self.snapshot, schema_version=2), "unsupported-schema"),
        ]:
            r = prospective_audit(self.rows, self.assignment, snap, self.cutoff)
            self.assertIn(reason, r.reasons)
            self.assertIsNone(r.audit)

    def test_naive_and_invalid_dates(self):
        for timestamp in ["2026-11-02", "2026-11-02T12:00:00", "not-a-time"]:
            with self.assertRaises(ValueError):
                prospective_audit(
                    self.rows,
                    self.assignment,
                    replace(self.snapshot, available_at=timestamp),
                    self.cutoff,
                )

    def test_offset_canonical_and_order(self):
        a = prospective_audit(self.rows, self.assignment, self.snapshot, self.cutoff)
        b = prospective_audit(
            list(reversed(self.rows)),
            dict(reversed(list(self.assignment.items()))),
            replace(
                self.snapshot,
                records=tuple(reversed(self.rows)),
                available_at="2026-11-02T07:00:00-05:00",
            ),
            self.cutoff,
        )
        self.assertEqual(a, b)
        self.assertEqual(utc("2026-11-02T07:00:00-05:00"), utc(self.cutoff))

    def test_hash_binds_assignment_source_and_times(self):
        a = prospective_audit(self.rows, self.assignment, self.snapshot, self.cutoff)
        variants = [
            replace(self.snapshot, source_id="other"),
            replace(self.snapshot, available_at="2026-11-02T11:00:00Z"),
        ]
        for snapshot in variants:
            b = prospective_audit(self.rows, self.assignment, snapshot, self.cutoff)
            self.assertNotEqual(a.manifest["input_sha256"], b.manifest["input_sha256"])
        b = prospective_audit(
            self.rows, {"a": "test", "b": "train"}, self.snapshot, self.cutoff
        )
        self.assertNotEqual(a.manifest["input_sha256"], b.manifest["input_sha256"])

    def test_manifest_integrity_not_authenticity(self):
        import copy

        r = prospective_audit(self.rows, self.assignment, self.snapshot, self.cutoff)
        self.assertTrue(verify_manifest(r.manifest))
        mutated = copy.deepcopy(r.manifest)
        mutated["payload"]["source_id"] = "tampered"
        self.assertFalse(verify_manifest(mutated))
        self.assertFalse(verify_manifest({}))
        self.assignment["a"] = "test"
        self.assertTrue(verify_manifest(r.manifest))

    def test_invalid_ids_assignment(self):
        with self.assertRaises(ValueError):
            prospective_audit(self.rows, {}, self.snapshot, self.cutoff)
        with self.assertRaises(ValueError):
            prospective_audit(
                self.rows,
                self.assignment,
                replace(self.snapshot, records=(Record("c", ("c",)),)),
                self.cutoff,
            )

    def test_backdating_cannot_be_authenticated(self):
        # False provenance can satisfy the syntax/policy: deliberately outside trust assumptions.
        r = prospective_audit(self.rows, self.assignment, self.snapshot, self.cutoff)
        self.assertEqual(r.status, "metadata-eligible")
        self.assertIn("no source authentication", str(r.manifest["scope"]))
