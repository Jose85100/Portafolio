"""Designed conformance matrix; no empirical leakage prevalence or model training."""

import csv
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from itertools import product
import json
import os
from pathlib import Path
import platform
import time
import tracemalloc
from src.partial_audit import partial_audit
from src.snapshot_gate import AdjudicationSnapshot, prospective_audit
from src.splitter import Record

OUT = Path("results/snapshot1102")


def run() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(Path("config_snapshot1102.json").read_text())
    cutoff = datetime.fromisoformat(cfg["cutoff"])
    observed = [Record(str(i), (f"i{i}",)) for i in range(8)]
    assignment = {str(i): "train" if i < 4 else "test" for i in range(8)}
    rows = []
    manifests = []
    for case, (
        complete,
        schema,
        source,
        effective_hours,
        available_hours,
        offset_hours,
    ) in enumerate(
        product(
            [True, False],
            [1, 2],
            ["synthetic-panel", ""],
            [-24, 0, 24],
            [-24, 0, 24],
            [0, -5],
        )
    ):
        zone = timezone(timedelta(hours=offset_hours))
        effective = (
            (cutoff + timedelta(hours=effective_hours)).astimezone(zone).isoformat()
        )
        available = (
            (cutoff + timedelta(hours=available_hours)).astimezone(zone).isoformat()
        )
        snapshot = AdjudicationSnapshot(
            tuple(observed),
            source,
            schema,
            "complete-equivalence-on-subset" if complete else "positive-links-only",
            effective,
            available,
        )
        # Independent oracle expressed on designed integers, not timestamp parser.
        expected = (
            complete
            and schema == 1
            and source != ""
            and effective_hours <= 0
            and available_hours <= 0
        )
        tracemalloc.start()
        start = time.perf_counter_ns()
        result = prospective_audit(observed, assignment, snapshot, cutoff.isoformat())
        elapsed = time.perf_counter_ns() - start
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        assert (result.status == "metadata-eligible") == expected
        manifests.append(dict(case=case, **asdict(result)))
        eligible = complete and schema == 1 and source != ""
        policies = {
            "ungated1101_misuse": True,
            "semantics_only": eligible,
            "event_time_only": eligible and effective_hours <= 0,
            "asof_reference": eligible
            and effective_hours <= 0
            and available_hours <= 0,
            "prospective_gate": result.status == "metadata-eligible",
            "abstain_all": False,
        }
        for policy, admitted in policies.items():
            rows.append(
                dict(
                    case=case,
                    policy=policy,
                    complete_equivalence=complete,
                    schema=schema,
                    source_present=bool(source),
                    effective_hours=effective_hours,
                    available_hours=available_hours,
                    offset_hours=offset_hours,
                    oracle_eligible=expected,
                    admitted=admitted,
                    false_admit=admitted and not expected,
                    false_reject=not admitted and expected,
                    elapsed_ns=elapsed if policy == "prospective_gate" else "",
                    peak_bytes=peak if policy == "prospective_gate" else "",
                )
            )
    with (OUT / "raw.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    summary = {}
    for policy in policies:
        subset = [r for r in rows if r["policy"] == policy]
        summary[policy] = {
            k: sum(bool(r[k]) for r in subset)
            for k in ["admitted", "false_admit", "false_reject"]
        }
        summary[policy]["cases"] = len(subset)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (OUT / "manifests.json").write_text(json.dumps(manifests, indent=2) + "\n")
    # Same instant in two offset encodings must hash identically for every case pair.
    assert all(
        manifests[i]["manifest"] == manifests[i + 1]["manifest"]
        for i in range(0, len(manifests), 2)
    )
    scale = []
    for n in cfg["scale_rows"]:
        obs = [Record(str(i), (f"i{i}",)) for i in range(n)]
        split = {str(i): "train" if i < n // 2 else "test" for i in range(n)}
        snap = AdjudicationSnapshot(
            tuple(obs),
            "synthetic-panel",
            1,
            "complete-equivalence-on-subset",
            cfg["cutoff"],
            cfg["cutoff"],
        )
        for repeat in range(3):
            tracemalloc.start()
            start = time.perf_counter_ns()
            r = prospective_audit(obs, split, snap, cfg["cutoff"])
            elapsed = time.perf_counter_ns() - start
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            assert r.audit is not None and r.audit.upper_exposed_rows == 0
            scale.append(
                dict(rows=n, repeat=repeat, elapsed_ns=elapsed, peak_bytes=peak)
            )
    (OUT / "scale.json").write_text(json.dumps(scale, indent=2) + "\n")
    env = dict(
        python=platform.python_version(),
        platform=platform.platform(),
        cpu_count=os.cpu_count(),
        cpu_model=next(
            (
                s.split(":", 1)[1].strip()
                for s in Path("/proc/cpuinfo").read_text().splitlines()
                if s.startswith("model name")
            ),
            "unknown",
        ),
    )
    (OUT / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    # Negative: metadata/semantics may be falsely declared. No authentication implied.
    snap = AdjudicationSnapshot(
        tuple(observed),
        "unverified-claimed-source",
        1,
        "complete-equivalence-on-subset",
        cfg["cutoff"],
        cfg["cutoff"],
    )
    false_claim = prospective_audit(observed, assignment, snap, cfg["cutoff"])
    truth = [Record(str(i), ("same-person",)) for i in range(8)]
    negative = dict(
        gate_status=false_claim.status,
        claimed_upper=partial_audit(observed, observed, assignment).upper_exposed_rows,
        actual_exposure=partial_audit(observed, truth, assignment).lower_exposed_rows,
        scope="outside trust assumptions: declarations and dates can lie; digest does not authenticate",
    )
    (OUT / "negative.json").write_text(json.dumps(negative, indent=2) + "\n")


if __name__ == "__main__":
    run()
