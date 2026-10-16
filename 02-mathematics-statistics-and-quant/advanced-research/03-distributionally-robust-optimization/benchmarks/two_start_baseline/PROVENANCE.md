# Provenance of the failed two-start experiment

`results.json` and `summary.csv` preserve the original failed execution's
aggregate measurements. Its complete original raw CSV was not retained: an
intermediate capture was truncated and has been removed rather than distributed
as valid data.

`replayed_raw.csv` is a fresh per-case reexecution of the same `two_start` variant,
datasets, seeds and radii. Its timing column is explicitly `replay_seconds` and
must not be presented as the original timings. Warning messages are grouped with
counts, not omitted. The final refined experiment's full raw CSV is independent
of this historical capture and is stored in `../raw.csv`.

Reproduce from the project directory:
```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts_replay_two_start.py
```
