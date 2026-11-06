#!/usr/bin/env python3
"""Repository-wide reproducible inventory of data provenance evidence.

Detects references to synthetic generation and real data sources by file.
A detection is an audit candidate, never proof that data were replaced.
Run from repo root: python tools/data_provenance_audit.py --output-dir /tmp/data-audit
"""
import argparse
import csv
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

EXTENSIONS = {".py", ".ipynb", ".r", ".jl", ".m", ".cpp", ".c", ".h", ".hpp", ".sql"}
SOURCE_REGEX = re.compile(r"\b(?:pd\.read_csv|read_csv|read_parquet|read_sql|fetch_ucirepo|yfinance|pandas_datareader|fredapi|world_bank|wbgapi|requests\.get|urlopen|download|socrata|quandl|datareader)\b|https?://", re.I)
SYNTHETIC_REGEX = re.compile(r"\b(?:make_classification|make_regression|make_blobs|default_rng|random\.normal|random\.uniform|random\.binomial|np\.random|rng\.normal|rng\.uniform|rng\.binomial|synthetic|sint[eé]tic|simula(?:te|tion|ci[oó]n)|mock_data|fake_data|faker)\b", re.I)
SEED_REGEX = re.compile(r"\b(?:random_state|seed|default_rng)\b", re.I)
EXPLICIT_REAL_REGEX = re.compile(r"\b(?:ucimlrepo|world.bank|banrep|dane|datos\.gov\.co|federalreserve|fred\.stlouisfed|sec\.gov|yfinance|stooq|alpha.vantage|suin-juriscol)\b", re.I)
EXCLUDE = (".git/", ".venv/", "venv/", "node_modules/", "build/", "dist/", "__pycache__/")


def tracked_files(repo: Path):
    process = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"],
                             capture_output=True, check=True)
    return [Path(x.decode("utf-8")) for x in process.stdout.split(b"\0") if x]


def code_only(path, raw):
    if path.suffix.lower() != ".ipynb":
        return raw
    notebook = json.loads(raw)
    return "\n".join("".join(cell.get("source", []))
                     for cell in notebook.get("cells", [])
                     if cell.get("cell_type") == "code")


def classify(path, content):
    synthetic = bool(SYNTHETIC_REGEX.search(content))
    source = bool(SOURCE_REGEX.search(content))
    explicit_real = bool(EXPLICIT_REAL_REGEX.search(content))
    if synthetic and (source or explicit_real):
        status = "MIXED_REVIEW"
    elif synthetic:
        status = "SYNTHETIC_CANDIDATE"
    elif source or explicit_real:
        status = "EXTERNAL_SOURCE_CANDIDATE"
    else:
        status = "NO_SIGNAL"
    domain = path.parts[0] if path.parts else "root"
    return {
        "path": path.as_posix(), "domain": domain,
        "synthetic_signal": int(synthetic),
        "external_source_signal": int(source or explicit_real),
        "seed_signal": int(bool(SEED_REGEX.search(content))),
        "audit_status": status,
        "verified_observed_integration": "NOT_VERIFIED",
        "review_required": "YES" if status != "NO_SIGNAL" else "LOW_PRIORITY",
    }


def run(repo, output_dir):
    repo = Path(repo).resolve()
    output_dir = Path(output_dir).resolve()
    inventory = []
    errors = []
    inspected = 0
    for path in tracked_files(repo):
        if path.suffix.lower() not in EXTENSIONS or any(path.as_posix().startswith(d) for d in EXCLUDE):
            continue
        inspected += 1
        try:
            content = code_only(path, (repo / path).read_text(encoding="utf-8"))
            inventory.append(classify(path, content))
        except (UnicodeError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            errors.append({"path": path.as_posix(), "error": str(exc)})
    inventory.sort(key=lambda r: r["path"])
    output_dir.mkdir(parents=True, exist_ok=True)
    fields = ["path", "domain", "synthetic_signal", "external_source_signal", "seed_signal",
              "audit_status", "verified_observed_integration", "review_required"]
    with (output_dir / "file_inventory.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(inventory)
    summary = {
        "tracked_code_files_inspected": inspected,
        "classified": len(inventory),
        "errors": errors,
        "by_status": dict(sorted(Counter(r["audit_status"] for r in inventory).items())),
        "by_domain_and_status": {k: dict(sorted(Counter(r["audit_status"] for r in inventory
                                                      if r["domain"] == k).items()))
                                 for k in sorted({r["domain"] for r in inventory})},
        "interpretation": "Static regex screening. A source reference is not an executed ingestion. "
                          "Synthetic simulation may be necessary for uncertainty and adversarial tests. "
                          "No verified integration is inferred by this inventory.",
        "coverage": "Tracked code and Jupyter code cells only; noncode assets and runtime-generated datasets excluded.",
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if errors:
        raise RuntimeError(f"{len(errors)} unreadable files, see summary.json")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.repo, args.output_dir), indent=2, ensure_ascii=False))
