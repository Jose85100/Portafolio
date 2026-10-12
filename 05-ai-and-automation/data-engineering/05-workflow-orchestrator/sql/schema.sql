-- PostgreSQL 15+: durable workflow executions with leasing semantics.
CREATE SCHEMA IF NOT EXISTS orchestration;
CREATE TABLE IF NOT EXISTS orchestration.task_runs (
 workflow_id TEXT NOT NULL,
 run_id TEXT NOT NULL,
 task_id TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('pending','running','succeeded','failed')),
 attempt INTEGER NOT NULL DEFAULT 0 CHECK(attempt >= 0),
 lease_until TIMESTAMPTZ,
 updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 error_message TEXT,
 PRIMARY KEY(workflow_id, run_id, task_id),
 CHECK(state <> 'running' OR lease_until IS NOT NULL)
);
CREATE INDEX IF NOT EXISTS pending_tasks_idx
 ON orchestration.task_runs(state, lease_until, updated_at);
-- Workers should claim work with SELECT ... FOR UPDATE SKIP LOCKED
-- inside a transaction, and use a stable idempotency key per side effect.
