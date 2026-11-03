import unittest

from src.audit_envelope import create_envelope, dumps_envelope, loads_envelope, verify_envelope
from src.dynamic import DynamicMoments
from src.transport import export_state


def sample_wire() -> str:
    state = DynamicMoments()
    for value in (1.0, 2.0, 3.0):
        state.push(value)
    return export_state(state)


class AuditEnvelopeTests(unittest.TestCase):
    def envelope(self, state: str = "unknown", counts=None):
        return create_envelope(
            sample_wire(), source_id="synthetic-fixture", partition_id="chunk-A",
            diagnostic_state=state, diagnostic_counts=counts,
        )

    def test_roundtrip_preserves_original_wire_and_unknown_is_null(self):
        document = self.envelope()
        restored = loads_envelope(dumps_envelope(document))
        self.assertEqual(verify_envelope(restored), sample_wire())
        self.assertEqual(set(restored["diagnostics"]["counts"].values()), {None})

    def test_tracked_zero_is_distinct_from_unknown(self):
        tracked = self.envelope("tracked", {"rounded_to_zero": 0, "normalization_failures": 0, "rebase_events": 0})
        unknown = self.envelope()
        self.assertEqual(tracked["diagnostics"]["counts"]["rounded_to_zero"], 0)
        self.assertIsNone(unknown["diagnostics"]["counts"]["rounded_to_zero"])

    def test_partial_requires_some_but_not_all_fields(self):
        doc = self.envelope("partial", {"rounded_to_zero": 2})
        self.assertEqual(doc["diagnostics"]["counts"], {
            "rounded_to_zero": 2, "normalization_failures": None, "rebase_events": None
        })

    def test_payload_tampering_is_rejected(self):
        doc = self.envelope()
        doc["payload"] += " "
        with self.assertRaises(ValueError):
            verify_envelope(doc)

    def test_metadata_tampering_is_rejected(self):
        doc = self.envelope()
        doc["provenance"]["partition_id"] = "different"
        with self.assertRaises(ValueError):
            verify_envelope(doc)

    def test_disjointness_cannot_be_asserted_as_verified(self):
        doc = self.envelope()
        doc["provenance"]["partition_claim"] = "verified_disjoint"
        with self.assertRaises(ValueError):
            verify_envelope(doc)

    def test_malformed_diagnostic_zero_cannot_be_marked_unknown(self):
        doc = self.envelope()
        doc["diagnostics"]["counts"]["rounded_to_zero"] = 0
        # Recompute the envelope digest to isolate the semantic check.
        unsigned = {key: value for key, value in doc.items() if key != "envelope_sha256"}
        from src.audit_envelope import _canonical_bytes, _digest
        doc["envelope_sha256"] = _digest(_canonical_bytes(unsigned))
        with self.assertRaises(ValueError):
            verify_envelope(doc)

    def test_invalid_v1_payload_rejected(self):
        with self.assertRaises(ValueError):
            create_envelope("MOMENTS_V2 1 0 0x0p+0 0x0p+0 0x0p+0 1", source_id="x", partition_id="y", diagnostic_state="unknown")

    def test_invalid_diagnostic_state_type_rejected(self):
        with self.assertRaises(ValueError):
            create_envelope(sample_wire(), source_id="x", partition_id="y", diagnostic_state=[])


if __name__ == "__main__":
    unittest.main()
