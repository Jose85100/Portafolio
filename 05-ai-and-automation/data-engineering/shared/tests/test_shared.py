import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from quality import evaluate
from point_in_time import asof_join
from reconciliation import reconcile
from evidence import manifest, verify

class SharedTests(unittest.TestCase):
    def test_quality_rules(self):
        rows = [{"id":"A","balance":"20","status":"active"},{"id":"A","balance":"-1","status":"unknown"}]
        report = evaluate(rows,[{"name":"unique_id","type":"unique","fields":["id"]},
                                {"name":"nonnegative","type":"range","field":"balance","min":0,"max":100},
                                {"name":"status","type":"allowed","field":"status","values":["active"]}])
        self.assertFalse(report["passed"])
        self.assertEqual(len(report["violations"]),3)

    def test_point_in_time_no_leakage(self):
        events = [{"entity_id":"A","decision_at":"2026-01-02T10:00:00"},
                  {"entity_id":"A","decision_at":"2026-01-03T10:00:00"}]
        feats = [{"entity_id":"A","available_at":"2026-01-02T09:00:00","score":10},
                 {"entity_id":"A","available_at":"2026-01-02T11:00:00","score":90}]
        result = asof_join(events,feats,feature_names=["score"])
        self.assertEqual([x["score"] for x in result],[10,90])

    def test_bitemporal_correction_is_not_visible_before_recording(self):
        events = [{"entity_id":"A", "decision_at":"2026-01-03T12:00:00+00:00"}]
        feats = [
            {"entity_id":"A", "available_at":"2026-01-01T00:00:00+00:00", "recorded_at":"2026-01-01T00:00:00+00:00", "valid_from":"2026-01-01T00:00:00+00:00", "score":10, "version":"v1"},
            {"entity_id":"A", "available_at":"2026-01-02T00:00:00+00:00", "recorded_at":"2026-01-04T00:00:00+00:00", "valid_from":"2026-01-01T00:00:00+00:00", "score":20, "version":"v2"},
        ]
        historical = asof_join(events, feats, feature_names=["score"], system_as_of="2026-01-03T12:00:00+00:00")
        corrected = asof_join(events, feats, feature_names=["score"], system_as_of="2026-01-05T00:00:00+00:00")
        self.assertEqual(historical[0]["score"], 10)
        self.assertEqual(corrected[0]["score"], 20)

    def test_timezone_mixing_and_expired_features_fail_or_exclude(self):
        with self.assertRaises(ValueError):
            asof_join([{"entity_id":"A", "decision_at":"2026-01-02T00:00:00"}],
                      [{"entity_id":"A", "available_at":"2026-01-01T00:00:00+00:00", "score":1}], feature_names=["score"])
        result = asof_join([{"entity_id":"A", "decision_at":"2026-01-03T00:00:00+00:00"}],
                           [{"entity_id":"A", "available_at":"2026-01-01T00:00:00+00:00", "valid_to":"2026-01-02T00:00:00+00:00", "score":1}],
                           feature_names=["score"])
        self.assertIsNone(result[0]["score"])

    def test_reconcile_single_date_not_sum_of_snapshots(self):
        rows = [{"loan_id":"A","as_of_date":"2026-01-01","principal":"100"},
                {"loan_id":"A","as_of_date":"2026-01-02","principal":"90"}]
        self.assertTrue(reconcile(rows,"2026-01-02","90")["passed"])
        self.assertFalse(reconcile(rows,"2026-01-02","100")["passed"])

    def test_evidence_tamper_detection(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d)/"a.txt"
            f.write_text("abc")
            report = manifest([f])
            self.assertTrue(verify(report))
            f.write_text("changed")
            self.assertFalse(verify(report))

    def test_invalid_rule_fails_closed(self):
        with self.assertRaises(ValueError):
            evaluate([], [{"name":"bad","type":"custom"}])

if __name__ == "__main__":
    unittest.main()
