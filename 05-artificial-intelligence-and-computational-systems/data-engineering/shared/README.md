# Shared Data Reliability Toolkit — implemented

Four reusable **Python standard-library** modules:
- `quality.py`: declarative uniqueness, null, allowed-values and numeric range checks.
- `point_in_time.py`: indexed as-of feature joins constrained by **availability timestamp**, bitemporal recording time and validity intervals.
- `reconciliation.py`: exact-decimal balance reconciliation at a **single snapshot date**.
- `evidence.py`: SHA256 evidence manifests and tamper detection.

Run `python3 -m unittest discover -s 05-ai-and-automation/data-engineering/shared/tests -v`.

## Availability contract

`decision_at`, `available_at`, `recorded_at`, `valid_from` and `valid_to` must be ISO-8601 timestamps. A join rejects a batch that mixes offset-aware and naïve timestamps. An all-naïve legacy batch is interpreted as UTC; new producers must emit an explicit offset (`Z` / `+00:00`). A feature may be selected only when:

$$available\_at \le decision\_at, \qquad recorded\_at \le system\_as\_of, \qquad valid\_from \le decision\_at < valid\_to$$

Missing `recorded_at` defaults to `available_at`; missing validity bounds are open-ended. This prevents a retroactive correction from appearing in a historical decision reconstruction before it was known.

**Limitations:** in-memory indexes, no distributed execution, no event-driven scheduling or schema registry. Production implementations require benchmarked scalability, metadata versioning, IAM and audit controls.
