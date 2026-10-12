# Risk Data Platform — executable MVP

**Status:** implemented local Python standard-library pipeline with unit tests. Not a production lakehouse.

## Run
```bash
python3 05-artificial-intelligence-and-computational-systems/data-engineering/risk-data-platform/src/pipeline.py \
  --source 05-artificial-intelligence-and-computational-systems/data-engineering/risk-data-platform/examples/loan_snapshots.csv \
  --snapshot-root /tmp/risk-snapshots
python3 -m unittest discover -s 05-artificial-intelligence-and-computational-systems/data-engineering/risk-data-platform/tests -v
```

## Features
Incremental upsert by `(loan_id, as_of_date)`, schema and financial invariants, duplicate conflict rejection, stable ordering, SHA256 output evidence, and reconciliation metrics. Every publication is an immutable `runs/<run_id>/` directory containing its CSV and manifest; only after hash verification does an atomic `current.json` pointer expose it. Optional `--rejects` writes diagnostics for invalid records.

## What it does **not** claim
No production SLA, no cloud deployment, no CDC, no Airflow/n8n execution, no point-in-time feature store, and no IFRS 9 ECL computation. See [architecture and contract](docs/ARCHITECTURE.md).
