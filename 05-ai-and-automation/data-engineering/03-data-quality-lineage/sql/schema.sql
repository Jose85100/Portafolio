-- PostgreSQL 15+: immutable checks and lineage edges.
CREATE SCHEMA IF NOT EXISTS governance;
CREATE TABLE IF NOT EXISTS governance.dataset_runs (
 run_id UUID PRIMARY KEY,
 dataset_name TEXT NOT NULL,
 dataset_version TEXT NOT NULL,
 source_sha256 CHAR(64) NOT NULL,
 started_at TIMESTAMPTZ NOT NULL,
 completed_at TIMESTAMPTZ,
 status TEXT NOT NULL CHECK(status IN ('running','passed','failed')),
 CONSTRAINT completed_run CHECK (status = 'running' OR completed_at IS NOT NULL)
);
CREATE TABLE IF NOT EXISTS governance.rule_results (
 run_id UUID NOT NULL REFERENCES governance.dataset_runs(run_id),
 rule_id TEXT NOT NULL,
 evaluated_rows BIGINT NOT NULL CHECK(evaluated_rows >= 0),
 failed_rows BIGINT NOT NULL CHECK(failed_rows >= 0 AND failed_rows <= evaluated_rows),
 PRIMARY KEY(run_id, rule_id)
);
CREATE TABLE IF NOT EXISTS governance.lineage_edges (
 run_id UUID NOT NULL REFERENCES governance.dataset_runs(run_id),
 upstream_dataset TEXT NOT NULL,
 downstream_dataset TEXT NOT NULL,
 PRIMARY KEY(run_id, upstream_dataset, downstream_dataset),
 CHECK(upstream_dataset <> downstream_dataset)
);
CREATE OR REPLACE VIEW governance.failed_rules AS
 SELECT r.run_id, d.dataset_name, r.rule_id, r.failed_rows,
        r.failed_rows::NUMERIC / NULLIF(r.evaluated_rows, 0) AS failure_rate
 FROM governance.rule_results r JOIN governance.dataset_runs d USING(run_id)
 WHERE r.failed_rows > 0;
