from __future__ import annotations
import csv
import json
import statistics
import time
from pathlib import Path
import matplotlib.pyplot as plt
from src.delta_replay import Delta, replay, snapshot_first

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/delta1104"
OUT.mkdir(parents=True, exist_ok=True)
rows = []
for n in (1, 10, 100, 1000):
    events = []
    for i in range(n):
        events.extend(
            [
                Delta(
                    f"e{i}",
                    "link",
                    "2026-01-01T00:00:00Z",
                    "2026-01-01T00:00:00Z",
                    f"l{i}",
                ),
                Delta(
                    f"e{i}",
                    "unlink",
                    "2026-01-02T00:00:00Z",
                    "2026-01-02T00:00:00Z",
                    f"u{i}",
                ),
                Delta(
                    f"e{i}",
                    "link",
                    "2026-01-01T12:00:00Z",
                    "2026-01-03T00:00:00Z",
                    f"c{i}",
                ),
            ]
        )
    kw = dict(identity_at="2026-01-03T00:00:00Z", cutoff="2026-01-05T00:00:00Z")
    expected = set()
    # Oracle: latest effective event among those available at cutoff is unlink.
    # The later-arriving correction only revises Jan-1 state; it cannot supersede Jan-2 unlink.

    got = replay(events, **kw)
    naive = snapshot_first(events, **kw)
    if got != expected:
        raise AssertionError("oracle mismatch")
    samples = []
    for _ in range(9):
        t = time.perf_counter_ns()
        replay(events, **kw)
        samples.append(time.perf_counter_ns() - t)
    rows.append(
        dict(
            events=len(events),
            correct_admits=len(got),
            oracle_admits=len(expected),
            false_admits=len(naive - expected),
            false_rejects=len(expected - naive),
            median_ns=int(statistics.median(samples)),
        )
    )
with (OUT / "raw.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0])
    w.writeheader()
    w.writerows(rows)
summary = {
    "synthetic": True,
    "seed": 1104,
    "rows": rows,
    "claim": "controlled semantics only; not empirical ML leakage measurement",
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(
    [r["events"] for r in rows],
    [r["median_ns"] for r in rows],
    marker="o",
    label="bitemporal replay",
)
ax.set(
    xscale="log",
    yscale="log",
    xlabel="Eventos sintéticos",
    ylabel="Mediana de replay (ns)",
    title="Costo de reconstrucción por ledger delta",
)
ax.grid(True, which="both", alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig(OUT / "replay_cost.png", dpi=150)
print(json.dumps(summary, sort_keys=True))
