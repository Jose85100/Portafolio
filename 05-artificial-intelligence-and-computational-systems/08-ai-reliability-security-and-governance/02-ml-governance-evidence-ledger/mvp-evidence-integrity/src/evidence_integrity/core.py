"""Small, offline verifier for declared ML evidence bundles (not an attestor)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Finding:
    code: str
    subject: str


@dataclass(frozen=True)
class Report:
    findings: tuple[Finding, ...]

    @property
    def valid(self) -> bool:
        return not self.findings


def digest_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_json(value: Any) -> bytes:
    """Deterministic subset serializer; excludes floats by contract."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def verify_bundle(root: Path) -> Report:
    """Check manifest shape, payload hashes, references and acyclic provenance DAG."""
    findings: list[Finding] = []
    try:
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return Report((Finding("manifest_unreadable", "manifest.json"),))
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema") != "evidence-bundle/v1"
        or not isinstance(manifest.get("artifacts"), list)
        or not isinstance(manifest.get("required_kinds", []), list)
        or not all(isinstance(x, str) for x in manifest.get("required_kinds", []))
    ):
        return Report((Finding("manifest_schema", "manifest.json"),))
    root = root.resolve()
    entries = manifest["artifacts"]
    by_id: dict[str, dict[str, Any]] = {}
    for item in entries:
        if not isinstance(item, dict) or not all(
            k in item for k in ("id", "path", "sha256", "depends_on", "kind")
        ):
            findings.append(Finding("artifact_schema", "unknown"))
            continue
        aid = item["id"]
        if not isinstance(aid, str) or aid in by_id:
            findings.append(Finding("duplicate_or_invalid_id", str(aid)))
            continue
        if (
            not isinstance(item["kind"], str)
            or not isinstance(item["sha256"], str)
            or len(item["sha256"]) != 64
            or any(c not in "0123456789abcdef" for c in item["sha256"])
        ):
            findings.append(Finding("artifact_schema", aid))
            continue
        by_id[aid] = item
        rel = item["path"]
        if (
            not isinstance(rel, str)
            or Path(rel).is_absolute()
            or ".." in Path(rel).parts
        ):
            findings.append(Finding("unsafe_path", str(aid)))
            continue
        candidate = root / rel
        # Reject symlinks at every component and verify the resolved path remains
        # beneath the bundle root. A production consumer must also avoid TOCTOU.
        current = root
        symlink = False
        for part in Path(rel).parts:
            current = current / part
            if current.is_symlink():
                symlink = True
                break
        if symlink:
            findings.append(Finding("unsafe_path", str(aid)))
            continue
        try:
            resolved = candidate.resolve(strict=True)
            resolved.relative_to(root)
            actual = digest_bytes(resolved.read_bytes())
        except (OSError, ValueError):
            findings.append(Finding("payload_missing", str(aid)))
            continue
        if actual != item["sha256"]:
            findings.append(Finding("digest_mismatch", str(aid)))
    required = set(manifest.get("required_kinds", []))
    present = {x.get("kind") for x in entries if isinstance(x, dict)}
    for kind in sorted(required - present):
        findings.append(Finding("required_kind_missing", str(kind)))
    graph: dict[str, list[str]] = {}
    for aid, item in by_id.items():
        deps = item["depends_on"]
        if not isinstance(deps, list) or not all(isinstance(dep, str) for dep in deps):
            findings.append(Finding("dependency_schema", aid))
            continue
        graph[aid] = []
        for dep in deps:
            if dep not in by_id:
                findings.append(Finding("dependency_missing", f"{aid}->{dep}"))
            else:
                graph[aid].append(dep)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            findings.append(Finding("provenance_cycle", node))
            return
        if node in visited:
            return
        visiting.add(node)
        for child in graph.get(node, []):
            visit(child)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)
    return Report(tuple(findings))
