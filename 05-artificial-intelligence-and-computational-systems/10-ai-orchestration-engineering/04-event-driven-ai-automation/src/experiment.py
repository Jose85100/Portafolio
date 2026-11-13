"""Paired deterministic workloads and a deliberately non-idempotent baseline."""
from __future__ import annotations
import random
import time
import tracemalloc
from dataclasses import dataclass
from .engine import Event, Inbox, valid

@dataclass(frozen=True)
class Workload:
    deliveries: tuple[Event, ...]
    fail_once: frozenset[str]
    oracle_count: int
    oracle_sum: int

def make_workload(seed: int, n: int = 120, duplicate_rate: float = 0.3,
                  invalid_rate: float = 0.05, conflict_rate: float = 0.05,
                  fault_rate: float = 0.15) -> Workload:
    if n < 1 or any(not 0 <= x <= 1 for x in
                    (duplicate_rate, invalid_rate, conflict_rate, fault_rate)):
        raise ValueError("invalid workload configuration")
    rng = random.Random(seed)
    base = [Event(f"evt-{seed}-{i}", rng.randrange(1, 100)) for i in range(n)]
    deliveries = list(base)
    for _ in range(round(n * duplicate_rate)):
        deliveries.append(rng.choice(base))
    for _ in range(round(n * conflict_rate)):
        chosen = rng.choice(base)
        deliveries.append(Event(chosen.event_id, chosen.amount + 100))
    for i in range(round(n * invalid_rate)):
        deliveries.append(Event(f"bad-{seed}-{i}", -1))
    rng.shuffle(deliveries)
    first_valid: dict[str, int] = {}
    for event in deliveries:
        if valid(event):
            first_valid.setdefault(event.event_id, event.amount)
    fail_once = frozenset(e.event_id for e in base if rng.random() < fault_rate)
    return Workload(tuple(deliveries), fail_once,
                    len(first_valid), sum(first_valid.values()))

def _p95(samples: list[float]) -> float:
    if not samples:
        return 0.0
    values = sorted(samples)
    return values[max(0, (95 * len(values) + 99) // 100 - 1)]

def run(workload: Workload, mode: str, replay: bool = True) -> dict[str, float | int | str]:
    if mode not in ("naive", "inbox", "inbox_no_retry"):
        raise ValueError(mode)
    timings: list[float] = []
    faulted: set[str] = set()
    backlog: list[Event] = []
    naive_count = 0
    naive_sum = 0
    invalid = 0
    inbox = Inbox() if mode != "naive" else None
    tracemalloc.start()
    t0 = time.perf_counter()
    try:
        for event in workload.deliveries:
            start = time.perf_counter_ns()
            if mode == "naive":
                if not valid(event):
                    invalid += 1
                elif event.event_id in workload.fail_once and event.event_id not in faulted:
                    faulted.add(event.event_id)
                    backlog.append(event)
                else:
                    naive_count += 1
                    naive_sum += event.amount
            else:
                assert inbox is not None
                inbox.receive(event, workload.fail_once)
            timings.append((time.perf_counter_ns() - start) / 1000)
        if mode == "naive":
            for event in backlog:
                naive_count += 1
                naive_sum += event.amount
            count, total = naive_count, naive_sum
            duplicates = 0
            conflicts = 0
            faults = len(faulted)
        else:
            assert inbox is not None
            if mode == "inbox":
                inbox.drain()
                inbox.assert_integrity()
            count, total = inbox.totals()
            duplicates, conflicts, invalid, faults = (
                inbox.duplicates, inbox.conflicts, inbox.invalid, inbox.faults
            )
        before_replay = total
        initial_duplicates = duplicates
        if replay:
            for event in workload.deliveries:
                if mode == "naive":
                    if valid(event):
                        naive_count += 1
                        naive_sum += event.amount
                else:
                    assert inbox is not None
                    inbox.receive(event)
            after_replay = naive_sum if mode == "naive" else inbox.totals()[1]
        else:
            after_replay = before_replay
        elapsed_ms = (time.perf_counter() - t0) * 1000
        _, peak = tracemalloc.get_traced_memory()
        return {
            "policy": mode,
            "deliveries": len(workload.deliveries),
            "expected_count": workload.oracle_count,
            "expected_sum": workload.oracle_sum,
            "actual_count": count,
            "actual_sum": total,
            "absolute_error": abs(total - workload.oracle_sum),
            "duplicate_effects": max(0, count - workload.oracle_count),
            "duplicates_prevented": initial_duplicates,
            "conflicts_rejected": conflicts,
            "dlq_count": invalid,
            "dlq_rate": invalid / len(workload.deliveries),
            "faults_injected": faults,
            "replay_delta": after_replay - before_replay,
            "pending": inbox.pending() if inbox else 0,
            "elapsed_ms": round(elapsed_ms, 4),
            "p95_delivery_us": round(_p95(timings), 3),
            "peak_kib": round(peak / 1024, 2),
        }
    finally:
        tracemalloc.stop()
        if inbox is not None:
            inbox.close()
