# Architecture decision record — Risk Data Platform MVP

## Layers
Physical (CSV snapshots / local filesystem) → Connectivity (CSV reader) → Virtual (schema and normalized rows) → Logical (deterministic upsert and reconciliation) → User (curated CSV + JSON manifest).

## Pipeline
```mermaid
flowchart LR
 A["Source CSV"] --> B["Contract validation"]
 B --> C["Keyed deduplication"]
 C --> D["Snapshot upsert"]
 D --> E["Curated CSV"]
 E --> F["SHA256 evidence manifest"]
 B --> G["Rejects on failure"]
```

## Data contract
- `loan_id`: nonempty string; `as_of_date`: ISO-8601 date; together form the immutable business key.
- `principal`: nonnegative finite decimal, two places; `days_past_due`: nonnegative integer.
- `status`: active, closed, default. Closed implies zero principal.
- `schema_version`: 1.0. Unknown columns and invalid values fail the batch.
- Repeated same-key records in one source must be identical. Later batches can update the same key.
- Historic snapshots are **not** summed to calculate a point-in-time outstanding balance; manifest sum is a sum across all stored snapshots, not a portfolio exposure metric.

## Reliability and limitations
- Deterministic ordering and SHA256 enable exact replay checks.
- Fail-closed on invalid records before publishing. Optional reject file includes line and reason.
- Atomic replacement is **per file**; CSV and manifest are not transactionally committed together. For production use immutable run directories and atomic pointer/snapshot manifests, plus locks for concurrent writers.
- This MVP does not provide CDC, database transactions, distributed storage, schema registry, IAM, encryption, scheduling, observability telemetry, SLA enforcement, data catalog or orchestration. These are subsequent milestones.
- Synthetic fixture only; no private or regulated data.
