import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from evidence_integrity import canonical_json, digest_bytes, verify_bundle


def bundle(root: Path) -> None:
    (root / "data.txt").write_text("input\n", encoding="utf-8")
    (root / "model.txt").write_text("weights\n", encoding="utf-8")
    manifest = {
        "schema": "evidence-bundle/v1",
        "required_kinds": ["dataset", "model"],
        "artifacts": [
            {
                "id": "data",
                "path": "data.txt",
                "sha256": digest_bytes(b"input\n"),
                "depends_on": [],
                "kind": "dataset",
            },
            {
                "id": "model",
                "path": "model.txt",
                "sha256": digest_bytes(b"weights\n"),
                "depends_on": ["data"],
                "kind": "model",
            },
        ],
    }
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


class VerifierTests(unittest.TestCase):
    def test_clean_and_tampered(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            bundle(p)
            self.assertTrue(verify_bundle(p).valid)
            (p / "model.txt").write_text("tampered", encoding="utf-8")
            self.assertIn(
                "digest_mismatch", {x.code for x in verify_bundle(p).findings}
            )

    def test_missing_kind_dependency_and_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            bundle(p)
            m = json.loads((p / "manifest.json").read_text())
            m["required_kinds"].append("approval")
            m["artifacts"][0]["depends_on"] = ["model"]
            (p / "manifest.json").write_text(json.dumps(m))
            codes = {f.code for f in verify_bundle(p).findings}
            self.assertIn("required_kind_missing", codes)
            self.assertIn("provenance_cycle", codes)

    def test_path_traversal_and_missing_payload(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            bundle(p)
            m = json.loads((p / "manifest.json").read_text())
            m["artifacts"][0]["path"] = "../secrets"
            m["artifacts"][1]["path"] = "gone"
            (p / "manifest.json").write_text(json.dumps(m))
            codes = {f.code for f in verify_bundle(p).findings}
            self.assertIn("unsafe_path", codes)
            self.assertIn("payload_missing", codes)

    def test_symlink_cannot_escape_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            p = base / "bundle"
            p.mkdir()
            outside = base / "outside.txt"
            outside.write_text("secret", encoding="utf-8")
            (p / "link.txt").symlink_to(outside)
            manifest = {
                "schema": "evidence-bundle/v1",
                "required_kinds": ["dataset"],
                "artifacts": [
                    {
                        "id": "external",
                        "path": "link.txt",
                        "sha256": digest_bytes(b"secret"),
                        "depends_on": [],
                        "kind": "dataset",
                    }
                ],
            }
            (p / "manifest.json").write_text(json.dumps(manifest))
            report = verify_bundle(p)
            self.assertFalse(report.valid)
            self.assertIn("unsafe_path", {f.code for f in report.findings})

    def test_malformed_dependency_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            bundle(p)
            m = json.loads((p / "manifest.json").read_text())
            m["artifacts"][0]["depends_on"] = [{}]
            (p / "manifest.json").write_text(json.dumps(m))
            self.assertIn(
                "dependency_schema", {x.code for x in verify_bundle(p).findings}
            )

    def test_malformed_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "manifest.json").write_text("{")
            self.assertEqual(verify_bundle(p).findings[0].code, "manifest_unreadable")

    def test_non_object_manifest_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "manifest.json").write_text("[]")
            self.assertEqual(verify_bundle(p).findings[0].code, "manifest_schema")

    def test_canonical_order_independent(self) -> None:
        for i in range(80):
            a = {f"k{j}": j + i for j in range(i % 9)}
            b = dict(reversed(list(a.items())))
            self.assertEqual(canonical_json(a), canonical_json(b))

    def test_hash_determinism_and_one_byte_sensitivity(self) -> None:
        for i in range(256):
            payload = f"case-{i}".encode()
            self.assertEqual(digest_bytes(payload), digest_bytes(payload))
            self.assertNotEqual(digest_bytes(payload), digest_bytes(payload + b"!"))


if __name__ == "__main__":
    unittest.main()
