-- PostgreSQL 15+: raw ledger, deduplicated point-in-time snapshot.
-- Monetary amounts use NUMERIC, never floating point.
CREATE SCHEMA IF NOT EXISTS credit;
CREATE TABLE IF NOT EXISTS credit.loan_events (
    source_system TEXT NOT NULL,
    event_id TEXT NOT NULL,
    loan_id TEXT NOT NULL,
    business_date DATE NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    principal NUMERIC(20, 2) NOT NULL CHECK (principal >= 0),
    days_past_due INTEGER NOT NULL CHECK (days_past_due >= 0),
    PRIMARY KEY (source_system, event_id)
);
CREATE INDEX IF NOT EXISTS loan_events_asof_idx
    ON credit.loan_events (loan_id, business_date DESC, ingested_at DESC);
CREATE OR REPLACE VIEW credit.latest_loan_position AS
WITH ranked AS (
 SELECT e.*, ROW_NUMBER() OVER (
  PARTITION BY loan_id ORDER BY business_date DESC, ingested_at DESC, event_id DESC
 ) AS row_number
 FROM credit.loan_events e WHERE business_date <= CURRENT_DATE - 1
)
SELECT loan_id, business_date, principal, days_past_due,
 CASE WHEN days_past_due = 0 THEN 'CURRENT'
      WHEN days_past_due <= 30 THEN 'DPD_01_30'
      WHEN days_past_due <= 60 THEN 'DPD_31_60'
      ELSE 'DPD_61_PLUS' END AS delinquency_bucket
FROM ranked WHERE row_number = 1;
-- For reproducible historical snapshots, replace CURRENT_DATE - 1
-- with a bound :as_of_date parameter in the consuming query.
