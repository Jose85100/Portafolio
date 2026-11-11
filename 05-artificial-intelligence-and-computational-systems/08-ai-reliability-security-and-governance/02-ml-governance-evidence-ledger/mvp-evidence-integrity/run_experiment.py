"""Deterministic adversarial simulation. No empirical/production data are used."""

from __future__ import annotations

import csv
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from evidence_integrity import digest_bytes, verify_bundle

ROOT = Path(__file__).parent
OUT = ROOT / "results"


def make_bundle(root: Path) -> None:
    (root / "data.csv").write_text("x,y\n0,0\n1,1\n", encoding="utf-8")
    (root / "weights.bin").write_bytes(b"simulated-weights-v1")
    (root / "approval.json").write_text(
        '{"status":"approved","actor":"fixture"}\n', encoding="utf-8"
    )
    items = [
        {
            "id": "dataset",
            "path": "data.csv",
            "sha256": digest_bytes((root / "data.csv").read_bytes()),
            "depends_on": [],
            "kind": "dataset",
        },
        {
            "id": "model",
            "path": "weights.bin",
            "sha256": digest_bytes((root / "weights.bin").read_bytes()),
            "depends_on": ["dataset"],
            "kind": "model",
        },
        {
            "id": "approval",
            "path": "approval.json",
            "sha256": digest_bytes((root / "approval.json").read_bytes()),
            "depends_on": ["model"],
            "kind": "approval",
        },
    ]
    (root / "manifest.json").write_text(
        json.dumps(
            {
                "schema": "evidence-bundle/v1",
                "required_kinds": ["dataset", "model", "approval"],
                "artifacts": items,
            }
        ),
        encoding="utf-8",
    )


def baseline(root: Path) -> bool:
    try:
        m = json.loads((root / "manifest.json").read_text())
        return m.get("schema") == "evidence-bundle/v1" and {
            x.get("kind") for x in m["artifacts"]
        } >= set(m["required_kinds"])
    except (OSError, json.JSONDecodeError, KeyError, TypeError, AttributeError):
        return False


def hash_only(root: Path) -> bool:
    try:
        m = json.loads((root / "manifest.json").read_text())
        return all(
            digest_bytes((root / x["path"]).read_bytes()) == x["sha256"]
            for x in m["artifacts"]
        )
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return False


def main() -> dict:
    OUT.mkdir(exist_ok=True)
    rows = []
    modes = (
        "clean",
        "payload_tamper",
        "missing_payload",
        "missing_dependency",
        "cycle",
        "rehash_after_tamper",
    )
    for case in range(40):
        for mode in modes:
            with tempfile.TemporaryDirectory() as d:
                p = Path(d)
                make_bundle(p)
                m = json.loads((p / "manifest.json").read_text())
                if mode == "payload_tamper":
                    (p / "weights.bin").write_bytes(b"attacker-changed")
                elif mode == "missing_payload":
                    (p / "weights.bin").unlink()
                elif mode == "missing_dependency":
                    m["artifacts"][1]["depends_on"] = ["ghost"]
                elif mode == "cycle":
                    m["artifacts"][0]["depends_on"] = ["model"]
                elif mode == "rehash_after_tamper":
                    (p / "weights.bin").write_bytes(b"attacker-changed")
                    m["artifacts"][1]["sha256"] = digest_bytes(
                        (p / "weights.bin").read_bytes()
                    )
                if mode in ("missing_dependency", "cycle", "rehash_after_tamper"):
                    (p / "manifest.json").write_text(json.dumps(m), encoding="utf-8")
                positives = mode == "clean"
                rows.append(
                    {
                        "seed_case": case,
                        "mode": mode,
                        "expected_valid": int(positives),
                        "baseline_valid": int(baseline(p)),
                        "hash_only_valid": int(hash_only(p)),
                        "full_valid": int(verify_bundle(p).valid),
                    }
                )
    with (OUT / "raw_cases.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    summary = []
    for mode in modes:
        group = [r for r in rows if r["mode"] == mode]
        summary.append(
            {
                "mode": mode,
                "n": len(group),
                "baseline_accept": sum(r["baseline_valid"] for r in group),
                "hash_only_accept": sum(r["hash_only_valid"] for r in group),
                "full_accept": sum(r["full_valid"] for r in group),
                "expected_accept": sum(r["expected_valid"] for r in group),
            }
        )
    result = {
        "experiment": "deterministic_manifest_mutation_simulation",
        "seed_cases": 40,
        "rows": len(rows),
        "data_status": "synthetic adversarial fixtures; not empirical observations",
        "summary": summary,
    }
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    try:
        import matplotlib.pyplot as plt

        labels = [x["mode"].replace("_", "\n") for x in summary]
        fig, ax = plt.subplots(figsize=(10, 5))
        xs = range(len(summary))
        ax.bar(
            [x - 0.24 for x in xs],
            [x["baseline_accept"] for x in summary],
            0.24,
            label="manifest-only baseline",
        )
        ax.bar(
            [x for x in xs],
            [x["hash_only_accept"] for x in summary],
            0.24,
            label="hash-only ablation",
        )
        ax.bar(
            [x + 0.24 for x in xs],
            [x["full_accept"] for x in summary],
            0.24,
            label="full verifier",
        )
        ax.set_xticks(list(xs), labels)
        ax.set_ylabel("accepted bundles (of 40)")
        ax.set_title("Synthetic mutation suite: acceptance by verifier")
        ax.legend()
        fig.tight_layout()
        fig.savefig(OUT / "acceptance.png", dpi=150)
        plt.close(fig)
    except ImportError:
        pass
    return result


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
