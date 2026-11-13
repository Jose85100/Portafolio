"""Designed synthetic test of revision ordering; no empirical ML outcome claim."""
from __future__ import annotations

import csv
import gzip
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import platform
import time
import tracemalloc

from src.temporal_revisions import Revision, filter_validity_first, select_full_replacements

OUT = Path("results/temporal1103")
BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def stamp(day: int) -> str:
    return (BASE + timedelta(days=day)).isoformat()


def histories() -> list[list[Revision]]:
    out = []
    for i in range(36):
        # New complete replacement supersedes the old open revision. The valid
        # intervals vary by entity to include active, expired and future cases.
        close_day = 9 + i % 3
        effective_day = 4 + i % 5
        out.append([
            Revision(f"e{i:02d}", "r0", stamp(0), stamp(0), None, f"old-{i}"),
            Revision(f"e{i:02d}", "r1", stamp(3), stamp(effective_day), stamp(close_day), f"replacement-{i}"),
            Revision(f"e{i:02d}", "r2", stamp(6), stamp(7 + i % 4), None, f"replacement2-{i}"),
        ])
    return out


def oracle(history: list[Revision], as_of: str, identity_at: str) -> tuple[str | None, str]:
    """Independent direct-sort reference implementation for one identity."""
    a = datetime.fromisoformat(as_of)
    t = datetime.fromisoformat(identity_at)
    known = sorted((r for r in history if datetime.fromisoformat(r.available_at) <= a), key=lambda r: datetime.fromisoformat(r.available_at), reverse=True)
    if not known:
        return None, "absent"
    selected = known[0]
    start = datetime.fromisoformat(selected.effective_at)
    end = datetime.fromisoformat(selected.valid_until) if selected.valid_until else None
    if start <= t and (end is None or t < end):
        return selected.revision_id, "eligible"
    return selected.revision_id, "not-effective-at-identity-time"


def run() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    hs = histories()
    rows: list[dict[str, object]] = []
    for history in hs:
        entity = history[0].identity
        for as_day in range(10):
            for target_day in (2, 6, 10):
                a, t = stamp(as_day), stamp(target_day)
                start = time.perf_counter_ns()
                tracemalloc.start()
                exact = select_full_replacements(history, as_of=a, identity_at=t)[0]
                elapsed = time.perf_counter_ns() - start
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                oracle_id, oracle_status = oracle(history, a, t)
                assert (exact.revision_id, exact.status) == (oracle_id, oracle_status)
                validity = filter_validity_first(history, as_of=a, identity_at=t)
                latest_known = max((r for r in history if datetime.fromisoformat(r.available_at) <= datetime.fromisoformat(a)), key=lambda r: r.available_at, default=None)
                latest_any = max(history, key=lambda r: r.available_at)
                policies = {
                    "latest_available_then_validity": exact.status == "eligible",
                    "validity_first_ablation": bool(validity),
                    "availability_only_ablation": latest_known is not None,
                    "ignore_availability_ablation": datetime.fromisoformat(latest_any.effective_at) <= datetime.fromisoformat(t) and (latest_any.valid_until is None or datetime.fromisoformat(t) < datetime.fromisoformat(latest_any.valid_until)),
                    "abstain_all": False,
                    "oracle": oracle_status == "eligible",
                }
                truth = oracle_status == "eligible"
                for policy, admitted in policies.items():
                    rows.append(dict(entity=entity, available_cutoff=a, identity_at=t, policy=policy,
                                     expected_revision=oracle_id or "", expected_status=oracle_status,
                                     admitted=admitted, false_admit=bool(admitted and not truth),
                                     false_reject=bool(not admitted and truth),
                                     elapsed_ns=elapsed if policy == "latest_available_then_validity" else "",
                                     peak_bytes=peak if policy == "latest_available_then_validity" else ""))
    with gzip.open(OUT / "raw.csv.gz", "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    summary: dict[str, dict[str, object]] = {}
    for policy in sorted({str(r["policy"]) for r in rows}):
        part = [r for r in rows if r["policy"] == policy]
        summary[policy] = {k: sum(bool(r[k]) for r in part) for k in ("admitted", "false_admit", "false_reject")}
        summary[policy]["queries"] = len(part)
    summary["design"] = {"histories": len(hs), "queries": 1080, "output_rows": len(rows), "synthetic": True, "seeds": [1103]}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    times = [int(str(r["elapsed_ns"])) for r in rows if r["elapsed_ns"] != ""]
    env = {"python": platform.python_version(), "platform": platform.platform(), "cpu_count": __import__("os").cpu_count(), "benchmark": "single-process synthetic query loop; includes Python allocations; not production throughput"}
    (OUT / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    peak_bytes = [int(str(r["peak_bytes"])) for r in rows if r["peak_bytes"] != ""]
    (OUT / "cost.json").write_text(json.dumps({"n": len(times), "median_ns": sorted(times)[len(times)//2], "p95_ns": sorted(times)[int(.95*(len(times)-1))], "max_peak_bytes": max(peak_bytes)}, indent=2) + "\n")
    # Deliberate counterexample: validity-first resurrects revision r0 although
    # a newer full replacement r1 is already known and is not valid at t=2.
    counter = [Revision("x", "r0", stamp(0), stamp(0), None, "old"), Revision("x", "r1", stamp(3), stamp(5), stamp(9), "new")]
    correct = select_full_replacements(counter, as_of=stamp(4), identity_at=stamp(2))[0]
    wrong = filter_validity_first(counter, as_of=stamp(4), identity_at=stamp(2))[0]
    (OUT / "counterexample.json").write_text(json.dumps({"latest_then_interval": correct.__dict__, "filter_interval_then_latest": wrong.__dict__, "interpretation": "A full replacement history selects r1 as the latest available revision; at identity_at=day 2 it is outside its valid interval, so it is ineligible. Filtering first improperly revives r0."}, indent=2) + "\n")
    assert summary["latest_available_then_validity"]["false_admit"] == 0


if __name__ == "__main__":
    run()
