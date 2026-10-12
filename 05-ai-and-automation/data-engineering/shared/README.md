# Shared Data Reliability Toolkit — implemented

Four reusable **Python standard-library** modules:
- `quality.py`: declarative uniqueness, null, allowed-values and numeric range checks.
- `point_in_time.py`: as-of feature joins constrained by **availability timestamp** to avoid leakage.
- `reconciliation.py`: exact-decimal balance reconciliation at a **single snapshot date**.
- `evidence.py`: SHA256 evidence manifests and tamper detection.

Run `python3 -m unittest discover -s 05-ai-and-automation/data-engineering/shared/tests -v`.

**Limitations:** in-memory algorithms, no distributed execution, no timezone normalization (use a consistent timezone), no bitemporal corrections, no event-driven scheduling or schema registry. Production implementations require benchmarked scalability, metadata versioning, IAM and audit controls.
