"""Content-addressed evidence for reproducible pipeline outputs."""
import hashlib
import json
from pathlib import Path

def manifest(paths):
    entries = []
    for path in sorted(map(Path, paths), key=lambda p: str(p)):
        payload = path.read_bytes()
        entries.append({"path": str(path), "bytes": len(payload),
                        "sha256": hashlib.sha256(payload).hexdigest()})
    return {"format_version": 1, "artifacts": entries}

def verify(report):
    return all(Path(x["path"]).exists() and
               hashlib.sha256(Path(x["path"]).read_bytes()).hexdigest() == x["sha256"]
               for x in report["artifacts"])
